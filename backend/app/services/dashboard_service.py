from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_audit_log import ChatAuditLog
from app.models.incident_ticket import IncidentTicket, TicketPriority, TicketStatus
from app.models.sop_document import IngestionStatus, SOPDocument


def _to_naive_utc(dt: datetime) -> datetime:
    """Chuẩn hóa datetime về UTC naive để tính hiệu thời gian an toàn trên cả SQLite và PostgreSQL."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


async def get_dashboard_kpi(db: AsyncSession) -> Dict[str, Any]:
    """
    Tính toán các chỉ số KPI vận hành cốt lõi của nhà máy:
    - Tài liệu SOP (Tổng / Đã nạp vector COMPLETED)
    - Phiếu sự cố (Tổng / Đang mở / Đã khắc phục / MTTR trung bình tính bằng phút)
    - Trợ lý RAG AI (Tổng lượt hỏi / TTFT trung bình / Tỷ lệ từ chối ngoài luồng)
    """
    total_sops = (await db.execute(select(func.count(SOPDocument.id)))).scalar_one() or 0
    indexed_sops = (
        await db.execute(
            select(func.count(SOPDocument.id)).where(
                SOPDocument.ingestion_status == IngestionStatus.COMPLETED
            )
        )
    ).scalar_one() or 0

    ticket_rows = (
        await db.execute(
            select(
                IncidentTicket.status,
                IncidentTicket.started_at,
                IncidentTicket.resolved_at,
            )
        )
    ).all()

    total_tickets = len(ticket_rows)
    open_tickets = sum(
        1 for row in ticket_rows if row.status in (TicketStatus.OPEN, TicketStatus.IN_PROGRESS)
    )
    resolved_tickets = sum(
        1 for row in ticket_rows if row.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED)
    )

    repair_durations_min: List[float] = []
    for row in ticket_rows:
        if row.started_at is not None and row.resolved_at is not None:
            diff_sec = (
                _to_naive_utc(row.resolved_at) - _to_naive_utc(row.started_at)
            ).total_seconds()
            if diff_sec >= 0:
                repair_durations_min.append(diff_sec / 60.0)

    mttr_minutes = (
        round(sum(repair_durations_min) / len(repair_durations_min), 2)
        if repair_durations_min
        else 0.0
    )

    chat_rows = (
        await db.execute(select(ChatAuditLog.is_refused, ChatAuditLog.ttft_ms))
    ).all()
    total_chat_queries = len(chat_rows)
    ttfts = [float(row.ttft_ms) for row in chat_rows if row.ttft_ms is not None]
    refused_count = sum(1 for row in chat_rows if row.is_refused)

    avg_ttft_ms = round(sum(ttfts) / len(ttfts), 2) if ttfts else 0.0
    refusal_rate_pct = (
        round((refused_count / total_chat_queries) * 100.0, 2)
        if total_chat_queries > 0
        else 0.0
    )

    return {
        "total_sops": int(total_sops),
        "indexed_sops": int(indexed_sops),
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
        "mttr_minutes": mttr_minutes,
        "total_chat_queries": total_chat_queries,
        "avg_ttft_ms": avg_ttft_ms,
        "refusal_rate_pct": refusal_rate_pct,
    }


async def get_dashboard_charts(db: AsyncSession) -> Dict[str, Any]:
    """
    Tổng hợp dữ liệu phục vụ biểu đồ Recharts trên Dashboard:
    - Sự cố phân bố theo tháng
    - Top 5 mã lỗi xuất hiện nhiều nhất
    - Phân bố sự cố theo trạng thái & mức độ ưu tiên
    - Top 5 tài liệu SOP được trợ lý AI trích dẫn nhiều nhất
    """
    ticket_rows = (
        await db.execute(
            select(
                IncidentTicket.created_at,
                IncidentTicket.error_code,
                IncidentTicket.status,
                IncidentTicket.priority,
            )
        )
    ).all()

    month_counter: Counter = Counter()
    error_counter: Counter = Counter()
    status_counter: Counter = Counter()
    priority_counter: Counter = Counter()

    for row in ticket_rows:
        if row.created_at:
            month_counter[row.created_at.strftime("%Y-%m")] += 1
        if row.error_code:
            error_counter[row.error_code] += 1
        status_val = row.status.value if hasattr(row.status, "value") else str(row.status)
        prio_val = row.priority.value if hasattr(row.priority, "value") else str(row.priority)
        status_counter[status_val] += 1
        priority_counter[prio_val] += 1

    incidents_by_month = [
        {"month": month, "count": count}
        for month, count in sorted(month_counter.items())
    ]
    top_error_codes = [
        {"error_code": code, "count": count}
        for code, count in error_counter.most_common(5)
    ]
    incidents_by_status = {s.value: status_counter.get(s.value, 0) for s in TicketStatus}
    incidents_by_priority = {p.value: priority_counter.get(p.value, 0) for p in TicketPriority}

    cited_rows = (await db.execute(select(ChatAuditLog.cited_doc_ids))).scalars().all()
    doc_cite_counter: Counter = Counter()
    for cited in cited_rows:
        if isinstance(cited, list):
            for doc_id in {str(d) for d in cited if d}:
                doc_cite_counter[doc_id] += 1

    top_doc_ids = [doc_id for doc_id, _ in doc_cite_counter.most_common(5)]
    top_cited_sops: List[Dict[str, Any]] = []
    if top_doc_ids:
        sops = (
            await db.execute(select(SOPDocument).where(SOPDocument.id.in_(top_doc_ids)))
        ).scalars().all()
        sop_map = {s.id: s for s in sops}
        for doc_id, count in doc_cite_counter.most_common(5):
            sop = sop_map.get(doc_id)
            top_cited_sops.append({
                "doc_id": doc_id,
                "document_code": sop.document_code if sop else "UNKNOWN",
                "title": sop.title if sop else "Tài liệu đã bị xóa",
                "citations": count,
            })

    return {
        "incidents_by_month": incidents_by_month,
        "top_error_codes": top_error_codes,
        "incidents_by_status": incidents_by_status,
        "incidents_by_priority": incidents_by_priority,
        "top_cited_sops": top_cited_sops,
    }
