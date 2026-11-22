import json
import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional

from fastapi import Request

from app.core.database import AsyncSessionLocal
from app.models.chat_audit_log import ChatAuditLog
from app.rag.citations import extract_verified_citations
from app.rag.llm.base import BaseLLMProvider
from app.rag.llm.factory import get_llm_provider
from app.rag.prompt_engine import REFUSAL_MESSAGE, build_rag_prompt
from app.rag.retriever import SOPRetriever, get_retriever
from app.schemas.chat import ChatQueryRequest

logger = logging.getLogger("smartsop.rag.streaming")


def format_sse_event(payload: Dict[str, Any]) -> str:
    """Đóng gói dictionary sự kiện thành chuẩn Server-Sent Events (`data: {...}\\n\\n`)."""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def _save_audit_log(
    session_factory: Any,
    *,
    user_id: Optional[str],
    question: str,
    answer: str,
    cited_doc_ids: List[str],
    cited_pages: List[int],
    top_score: float,
    is_refused: bool,
    ttft_ms: Optional[int],
    latency_ms: int,
    is_partial: bool,
) -> Optional[str]:
    """Lưu nhật ký kiểm toán hỏi đáp vào bảng `chat_audit_logs` mà không làm sập luồng stream."""
    try:
        async with session_factory() as db:
            log_entry = ChatAuditLog(
                user_id=user_id,
                question=question[:1000],
                answer=answer,
                cited_doc_ids=cited_doc_ids,
                cited_pages=cited_pages,
                top_score=top_score,
                is_refused=is_refused,
                ttft_ms=ttft_ms,
                latency_ms=latency_ms,
                is_partial=is_partial,
            )
            db.add(log_entry)
            await db.commit()
            await db.refresh(log_entry)
            return log_entry.id
    except Exception as exc:
        logger.warning(f"Không thể ghi chat_audit_logs: {exc}")
        return None


async def stream_rag_response(
    request: Optional[Request],
    query_in: ChatQueryRequest,
    user_id: Optional[str],
    retriever: Optional[SOPRetriever] = None,
    llm_provider: Optional[BaseLLMProvider] = None,
    session_factory: Any = None,
) -> AsyncIterator[str]:
    """
    Điều phối toàn trình RAG Streaming qua SSE:
    1. Truy hồi Dual-Retrieval (`aretrieve`).
    2. Nếu ngoài phạm vi (`is_out_of_domain`), từ chối tức thì không gọi LLM (tiết kiệm token).
    3. Stream token từ LLM kèm kiểm tra `request.is_disconnected()` và đo TTFT / Latency.
    4. Đối soát trích dẫn thực tế (`citation` events), ghi `chat_audit_logs`, và gửi `done`.
    """
    start_ts = time.perf_counter()
    active_retriever = retriever or get_retriever()
    factory = session_factory or AsyncSessionLocal

    answer_parts: List[str] = []
    ttft_ms: Optional[int] = None
    is_partial = False
    top_score = 0.0
    detected_codes: List[str] = []

    try:
        ret = await active_retriever.aretrieve(
            query_in.question,
            top_k=query_in.top_k,
            doc_id=query_in.doc_id,
        )
        top_score = float(ret.get("top_score", 0.0))
        detected_codes = list(ret.get("detected_error_codes") or [])
        chunks = ret.get("chunks") or []

        # Từ chối nhanh khi không vượt ngưỡng tương đồng (không khởi tạo hoặc gọi LLM)
        if ret.get("is_out_of_domain") or not chunks:
            ttft_ms = int((time.perf_counter() - start_ts) * 1000)
            yield format_sse_event({"type": "token", "content": REFUSAL_MESSAGE})
            latency_ms = int((time.perf_counter() - start_ts) * 1000)
            audit_id = await _save_audit_log(
                factory,
                user_id=user_id,
                question=query_in.question,
                answer=REFUSAL_MESSAGE,
                cited_doc_ids=[],
                cited_pages=[],
                top_score=top_score,
                is_refused=True,
                ttft_ms=ttft_ms,
                latency_ms=latency_ms,
                is_partial=False,
            )
            yield format_sse_event({
                "type": "done",
                "audit_log_id": audit_id,
                "is_refused": True,
                "ttft_ms": ttft_ms,
                "latency_ms": latency_ms,
                "total_chars": len(REFUSAL_MESSAGE),
                "top_score": top_score,
                "detected_error_codes": detected_codes,
            })
            return

        active_llm = llm_provider or get_llm_provider()
        prompt_pack = build_rag_prompt(query_in.question, chunks)

        async for token in active_llm.astream(
            system_prompt=prompt_pack["system_prompt"],
            user_prompt=prompt_pack["user_prompt"],
            temperature=query_in.temperature,
        ):
            if request is not None and await request.is_disconnected():
                is_partial = True
                logger.info("Client đã ngắt kết nối SSE, dừng sinh token sớm.")
                break

            if not token:
                continue

            if ttft_ms is None:
                ttft_ms = int((time.perf_counter() - start_ts) * 1000)
            answer_parts.append(token)
            yield format_sse_event({"type": "token", "content": token})

        full_answer = "".join(answer_parts)
        is_refused = (REFUSAL_MESSAGE in full_answer) or (not full_answer.strip())
        citations = (
            []
            if (is_refused or is_partial)
            else extract_verified_citations(full_answer, chunks)
        )

        if not is_partial:
            for citation in citations:
                yield format_sse_event({"type": "citation", **citation})

        latency_ms = int((time.perf_counter() - start_ts) * 1000)
        cited_doc_ids = [c["doc_id"] for c in citations if c.get("doc_id")]
        cited_pages = [int(c["page"]) for c in citations]

        audit_id = await _save_audit_log(
            factory,
            user_id=user_id,
            question=query_in.question,
            answer=full_answer,
            cited_doc_ids=cited_doc_ids,
            cited_pages=cited_pages,
            top_score=top_score,
            is_refused=is_refused,
            ttft_ms=ttft_ms,
            latency_ms=latency_ms,
            is_partial=is_partial,
        )

        if not is_partial:
            yield format_sse_event({
                "type": "done",
                "audit_log_id": audit_id,
                "is_refused": is_refused,
                "ttft_ms": ttft_ms,
                "latency_ms": latency_ms,
                "total_chars": len(full_answer),
                "top_score": top_score,
                "detected_error_codes": detected_codes,
            })

    except Exception as exc:
        logger.exception(f"Lỗi trong luồng SSE RAG streaming: {exc}")
        latency_ms = int((time.perf_counter() - start_ts) * 1000)
        partial_answer = "".join(answer_parts) or f"[ERROR] {exc}"
        await _save_audit_log(
            factory,
            user_id=user_id,
            question=query_in.question,
            answer=partial_answer,
            cited_doc_ids=[],
            cited_pages=[],
            top_score=top_score,
            is_refused=False,
            ttft_ms=ttft_ms,
            latency_ms=latency_ms,
            is_partial=True,
        )
        yield format_sse_event({"type": "error", "detail": str(exc)})
