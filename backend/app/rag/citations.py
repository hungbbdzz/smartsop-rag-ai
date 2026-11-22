from pathlib import Path
import re
from typing import Any, Dict, List, Tuple

from app.rag.prompt_engine import REFUSAL_MESSAGE

# Bắt thẻ trích dẫn dạng [SOP_FEEDER_004.pdf - Trang 1], [SOP_SMT_001 - Page 2], [SOP-FEEDER-004-VN, Tr. 1]
CITATION_PATTERN = re.compile(
    r"\[([^\[\]\n]+?)\s*[-–,]\s*(?:Trang|Page|Tr\.?)\s*(\d+)\]",
    re.IGNORECASE,
)


def _snippet(text: str, max_len: int = 220) -> str:
    compact = re.sub(r"\s+", " ", (text or "").strip())
    if len(compact) <= max_len:
        return compact
    return compact[: max_len - 3].rstrip() + "..."


def _build_chunk_lookup(
    retrieved_chunks: List[Dict[str, Any]],
) -> Dict[Tuple[str, int], Dict[str, Any]]:
    """
    Lập chỉ mục các chunk thực tế đã truy hồi theo cặp (tên_file_hoặc_mã, số_trang)
    để đối soát loại bỏ mọi trích dẫn bịa đặt từ LLM.
    """
    lookup: Dict[Tuple[str, int], Dict[str, Any]] = {}

    for chunk in retrieved_chunks:
        meta = chunk.get("metadata") or {}
        source_file = str(meta.get("source_file") or chunk.get("source_file") or "").strip()
        doc_code = str(meta.get("doc_code") or "").strip()
        page_num = int(meta.get("page_num") or chunk.get("page_number") or 0)
        if not source_file or page_num <= 0:
            continue

        keys = [
            (source_file.lower(), page_num),
            (Path(source_file).stem.lower(), page_num),
        ]
        if doc_code:
            keys.append((doc_code.lower(), page_num))

        score = float(chunk.get("score", 0.0))
        for key in keys:
            existing = lookup.get(key)
            if existing is None or score > float(existing.get("score", 0.0)):
                lookup[key] = chunk

    return lookup


def _format_citation(chunk: Dict[str, Any]) -> Dict[str, Any]:
    meta = chunk.get("metadata") or {}
    source_file = str(meta.get("source_file") or chunk.get("source_file") or "")
    page_num = int(meta.get("page_num") or chunk.get("page_number") or 1)
    return {
        "doc_id": str(meta.get("doc_id") or ""),
        "doc_code": str(meta.get("doc_code") or ""),
        "file": source_file,
        "page": page_num,
        "section_title": str(meta.get("section_title") or chunk.get("section_title") or ""),
        "score": round(float(chunk.get("score", 0.0)), 4),
        "snippet": _snippet(chunk.get("content") or ""),
    }


def extract_verified_citations(
    answer_text: str,
    retrieved_chunks: List[Dict[str, Any]],
    fallback_to_retrieved: bool = True,
) -> List[Dict[str, Any]]:
    """
    Đối soát các thẻ trích dẫn `[Tên file - Trang X]` trong câu trả lời của LLM với
    danh sách chunk thực tế đã truy hồi:
    - Trả về `[]` ngay nếu không có ngữ cảnh hoặc câu trả lời là từ chối chuẩn (`REFUSAL_MESSAGE`).
    - Loại bỏ hoàn toàn mọi trích dẫn sai tên file hoặc sai số trang (chống ảo giác).
    - Nếu LLM quên ghi thẻ nhưng có ngữ cảnh hợp lệ và `fallback_to_retrieved=True`, trả về nguồn từ `retrieved_chunks`.
    """
    if not retrieved_chunks or (answer_text and REFUSAL_MESSAGE in answer_text):
        return []

    lookup = _build_chunk_lookup(retrieved_chunks)
    verified: List[Dict[str, Any]] = []
    seen_canonical = set()

    for match in CITATION_PATTERN.finditer(answer_text or ""):
        file_ref = match.group(1).strip().lower()
        page_num = int(match.group(2))

        matched_chunk = lookup.get((file_ref, page_num))
        if not matched_chunk:
            matched_chunk = lookup.get((Path(file_ref).stem.lower(), page_num))
        if not matched_chunk:
            continue

        citation = _format_citation(matched_chunk)
        canonical_key = (citation["doc_id"] or citation["file"].lower(), citation["page"])
        if canonical_key not in seen_canonical:
            seen_canonical.add(canonical_key)
            verified.append(citation)

    if not verified and fallback_to_retrieved:
        for chunk in retrieved_chunks:
            citation = _format_citation(chunk)
            if not citation["file"]:
                continue
            canonical_key = (citation["doc_id"] or citation["file"].lower(), citation["page"])
            if canonical_key not in seen_canonical:
                seen_canonical.add(canonical_key)
                verified.append(citation)

    return verified


def strip_unverified_citations(
    answer_text: str,
    retrieved_chunks: List[Dict[str, Any]],
) -> str:
    """
    Xóa khỏi văn bản trả lời bất kỳ thẻ `[Tên file - Trang X]` nào không khớp với chunk đã truy hồi,
    giữ nguyên các thẻ trích dẫn hợp lệ.
    """
    if not answer_text:
        return ""

    lookup = _build_chunk_lookup(retrieved_chunks)

    def _replace_match(match: re.Match) -> str:
        file_ref = match.group(1).strip().lower()
        page_num = int(match.group(2))
        if (file_ref, page_num) in lookup or (Path(file_ref).stem.lower(), page_num) in lookup:
            return match.group(0)
        return ""

    cleaned = CITATION_PATTERN.sub(_replace_match, answer_text)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([.,;:])", r"\1", cleaned)
    return cleaned.strip()
