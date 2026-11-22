import logging
import re
import threading
from typing import Any, Dict, List, Optional

from fastapi.concurrency import run_in_threadpool

from app.core.config import settings
from app.rag.vector_store import VectorStoreService, get_vector_store

logger = logging.getLogger("smartsop.rag.retriever")

# Nhận diện mã lỗi & mã khuyết tật công nghiệp (E-204, ALM-03, ERR-12, T-102, A-105, R-088, PCB-D02...)
ERROR_CODE_PATTERN = re.compile(
    r"\b(?:E|ALM|ERR|T|A|R)-\d{2,4}\b|\bPCB-D\d{2,3}\b",
    re.IGNORECASE,
)

_retriever_lock = threading.Lock()
_retriever_instance: Optional["SOPRetriever"] = None


def extract_error_codes(query: str) -> List[str]:
    """
    Trích xuất danh sách mã lỗi / mã khuyết tật kỹ thuật từ câu hỏi (chuẩn hóa in hoa, loại trùng).
    """
    if not query:
        return []
    seen = set()
    codes: List[str] = []
    for match in ERROR_CODE_PATTERN.finditer(query):
        code = match.group(0).upper()
        if code not in seen:
            seen.add(code)
            codes.append(code)
    return codes


class SOPRetriever:
    """
    Bộ máy truy hồi kép (Dual-Retrieval) kết hợp:
    1. Tìm kiếm ngữ nghĩa Dense Cosine Search qua ChromaDB.
    2. Bắt chính xác mã lỗi kỹ thuật (Regex Error-Code Boost) để không bỏ sót bảng tra cứu.
    3. Cổng lọc ngưỡng tương đồng `SIMILARITY_THRESHOLD` giúp chặn câu hỏi ngoài phạm vi sớm.
    """

    def __init__(
        self,
        vector_store: Optional[VectorStoreService] = None,
        similarity_threshold: Optional[float] = None,
    ) -> None:
        self._vector_store = vector_store
        self.similarity_threshold = (
            settings.SIMILARITY_THRESHOLD
            if similarity_threshold is None
            else float(similarity_threshold)
        )

    def _get_vs(self) -> VectorStoreService:
        return self._vector_store or get_vector_store()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        doc_id: Optional[str] = None,
        threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Truy hồi các đoạn SOP liên quan nhất kèm điểm tương đồng và cờ ngoài phạm vi (`is_out_of_domain`).
        """
        if not query or not query.strip():
            return {
                "query": query,
                "detected_error_codes": [],
                "chunks": [],
                "top_score": 0.0,
                "is_out_of_domain": True,
                "retrieval_mode": "empty",
            }

        eff_threshold = self.similarity_threshold if threshold is None else float(threshold)
        error_codes = extract_error_codes(query)
        vs = self._get_vs()
        where_filter = {"doc_id": doc_id} if doc_id else None

        dense_results = vs.query(
            query_text=query,
            top_k=max(top_k * 2, 10),
            where=where_filter,
        )

        merged: Dict[str, Dict[str, Any]] = {}
        for item in dense_results:
            cid = item["chroma_id"]
            merged[cid] = {
                "chroma_id": cid,
                "content": item["content"],
                "score": round(float(item["score"]), 4),
                "metadata": item.get("metadata") or {},
                "match_type": "semantic",
            }

        if error_codes and vs.count() > 0:
            code_patterns = [
                (code, re.compile(rf"\b{re.escape(code)}\b", re.IGNORECASE))
                for code in error_codes
            ]
            all_items = vs.collection.get(
                where=where_filter,
                include=["documents", "metadatas"],
            )
            raw_ids = all_items.get("ids") or []
            raw_docs = all_items.get("documents") or []
            raw_metas = all_items.get("metadatas") or []

            for cid, doc_text, meta in zip(raw_ids, raw_docs, raw_metas):
                text_val = doc_text or ""
                matched = [code for code, pat in code_patterns if pat.search(text_val)]
                if not matched:
                    continue

                if cid in merged:
                    existing = merged[cid]
                    existing["score"] = min(
                        1.0, round(max(existing["score"] + 0.25, 0.85), 4)
                    )
                    existing["match_type"] = "hybrid_exact"
                    existing["matched_error_codes"] = matched
                else:
                    merged[cid] = {
                        "chroma_id": cid,
                        "content": text_val,
                        "score": 0.85,
                        "metadata": meta or {},
                        "match_type": "exact_error_code",
                        "matched_error_codes": matched,
                    }

        sorted_results = sorted(
            merged.values(),
            key=lambda r: (
                r["score"],
                1 if r.get("match_type") != "semantic" else 0,
                1 if (r.get("metadata") or {}).get("is_table") else 0,
            ),
            reverse=True,
        )
        top_results = sorted_results[:top_k]
        top_score = round(float(top_results[0]["score"]), 4) if top_results else 0.0
        qualified = [r for r in top_results if r["score"] >= eff_threshold]

        return {
            "query": query,
            "detected_error_codes": error_codes,
            "chunks": qualified,
            "top_score": top_score,
            "is_out_of_domain": len(qualified) == 0,
            "retrieval_mode": "dual_hybrid" if error_codes else "semantic",
        }

    async def aretrieve(
        self,
        query: str,
        top_k: int = 5,
        doc_id: Optional[str] = None,
        threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Phiên bản bất đồng bộ chạy truy hồi trong threadpool để không block FastAPI event loop."""
        return await run_in_threadpool(
            self.retrieve,
            query,
            top_k=top_k,
            doc_id=doc_id,
            threshold=threshold,
        )


def get_retriever() -> SOPRetriever:
    """Trả về instance Singleton duy nhất của SOPRetriever."""
    global _retriever_instance
    if _retriever_instance is None:
        with _retriever_lock:
            if _retriever_instance is None:
                _retriever_instance = SOPRetriever()
    return _retriever_instance
