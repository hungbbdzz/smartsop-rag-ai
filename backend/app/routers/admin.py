from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.chat_audit_log import ChatAuditLog
from app.models.incident_ticket import IncidentTicket
from app.models.machine import Machine
from app.models.production_line import ProductionLine
from app.models.sop_chunk import SOPChunk
from app.models.sop_document import SOPDocument
from app.models.user import User, UserRole
from app.rag.llm.factory import get_llm_provider
from app.rag.vector_store import get_vector_store

# Nhóm API Quản trị & Giám sát hệ thống: CHỈ ADMIN MỚI ĐƯỢC PHÉP
router = APIRouter(
    prefix="/admin",
    tags=["System Administration"],
    dependencies=[Depends(require_roles([UserRole.ADMIN]))],
)


@router.get(
    "/audit_logs",
    summary="Xem nhật ký kiểm toán hỏi đáp Trợ lý RAG AI (Hỗ trợ lọc câu hỏi bị từ chối)",
)
async def list_chat_audit_logs(
    is_refused: Optional[bool] = Query(None, description="Lọc theo trạng thái từ chối (True/False)"),
    user_id: Optional[str] = Query(None, description="Lọc theo ID nhân viên đặt câu hỏi"),
    limit: int = Query(50, ge=1, le=200, description="Số bản ghi tối đa trả về"),
    offset: int = Query(0, ge=0, description="Vị trí bắt đầu phân trang"),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if is_refused is not None:
        filters.append(ChatAuditLog.is_refused == is_refused)
    if user_id:
        filters.append(ChatAuditLog.user_id == user_id)

    total = (
        await db.execute(select(func.count(ChatAuditLog.id)).where(*filters))
    ).scalar_one() or 0

    rows = (
        await db.execute(
            select(ChatAuditLog)
            .where(*filters)
            .order_by(ChatAuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
    ).scalars().all()

    items = [
        {
            "id": row.id,
            "user_id": row.user_id,
            "question": row.question,
            "answer": row.answer,
            "cited_doc_ids": row.cited_doc_ids or [],
            "cited_pages": row.cited_pages or [],
            "top_score": row.top_score,
            "is_refused": row.is_refused,
            "ttft_ms": row.ttft_ms,
            "latency_ms": row.latency_ms,
            "is_partial": row.is_partial,
            "feedback_rating": row.feedback_rating,
            "created_at": row.created_at,
        }
        for row in rows
    ]

    return {
        "total": int(total),
        "limit": limit,
        "offset": offset,
        "items": items,
    }


@router.get(
    "/system_status",
    summary="Kiểm tra tình trạng kết nối CSDL, kho vector ChromaDB và mô hình LLM",
)
async def read_system_status(db: AsyncSession = Depends(get_db)):
    db_status: Dict[str, Any] = {"status": "ok"}
    counts: Dict[str, int] = {}
    try:
        await db.execute(text("SELECT 1"))
        count_queries = [
            ("users", User.id),
            ("production_lines", ProductionLine.id),
            ("machines", Machine.id),
            ("sop_documents", SOPDocument.id),
            ("sop_chunks", SOPChunk.id),
            ("incident_tickets", IncidentTicket.id),
            ("chat_audit_logs", ChatAuditLog.id),
        ]
        for key, col in count_queries:
            counts[key] = int((await db.execute(select(func.count(col)))).scalar_one() or 0)
    except Exception as exc:
        db_status = {"status": "error", "detail": str(exc)}

    def _inspect_vectors() -> Dict[str, Any]:
        vs = get_vector_store()
        return {
            "status": "ok",
            "collection": vs.collection_name,
            "vector_count": vs.count(),
        }

    try:
        vector_status = await run_in_threadpool(_inspect_vectors)
    except Exception as exc:
        vector_status = {"status": "error", "detail": str(exc), "vector_count": 0}

    try:
        llm_status = await get_llm_provider().health_check()
    except Exception as exc:
        llm_status = {"status": "error", "detail": str(exc)}

    overall_ok = db_status["status"] == "ok" and vector_status["status"] == "ok"
    return {
        "status": "ok" if overall_ok else "degraded",
        "database": db_status,
        "vector_store": vector_status,
        "llm": llm_status,
        "counts": counts,
    }
