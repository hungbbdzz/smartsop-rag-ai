import logging
import re
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sop_document import SOPDocument
from app.rag.retriever import SOPRetriever, get_retriever

logger = logging.getLogger("smartsop.services.ticket_service")


def _truncate_snippet(text: str, max_len: int = 450) -> str:
    compact = re.sub(r"\s+", " ", (text or "").strip())
    if len(compact) <= max_len:
        return compact
    return compact[: max_len - 3].rstrip() + "..."


async def suggest_sop_for_incident(
    error_code: str,
    description: str,
    db: AsyncSession,
    retriever: Optional[SOPRetriever] = None,
    threshold: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """
    Tìm kiếm nhanh tài liệu SOP phù hợp nhất với mã lỗi & mô tả sự cố máy móc.
    Đảm bảo đối chiếu `doc_id` còn tồn tại trong bảng `sop_documents` trước khi gán FK.
    Nếu hệ thống vector chưa có dữ liệu hoặc gặp lỗi kết nối, trả về `None` để không chặn tạo phiếu.
    """
    query = f"{error_code or ''} {description or ''}".strip()
    if not query:
        return None

    try:
        active_retriever = retriever or get_retriever()
        ret = await active_retriever.aretrieve(query, top_k=3, threshold=threshold)
    except Exception as exc:
        logger.warning(f"Lỗi khi gợi ý SOP tự động cho sự cố ({error_code}): {exc}")
        return None

    chunks = ret.get("chunks") or []
    if ret.get("is_out_of_domain") or not chunks:
        return None

    for chunk in chunks:
        meta = chunk.get("metadata") or {}
        doc_id = str(meta.get("doc_id") or "").strip()
        if not doc_id:
            continue

        res = await db.execute(select(SOPDocument).where(SOPDocument.id == doc_id))
        sop = res.scalar_one_or_none()
        if not sop:
            continue

        return {
            "suggested_sop_id": sop.id,
            "document_code": sop.document_code,
            "title": sop.title,
            "file_name": sop.file_name,
            "suggested_page": int(meta.get("page_num") or 1),
            "suggested_snippet": _truncate_snippet(chunk.get("content") or "", max_len=450),
            "score": round(float(chunk.get("score", 0.0)), 4),
        }

    return None
