"""
Unit test suite cho Milestone 3.1 - Phần 1 (Dual-Retrieval Engine):
- Bắt mã lỗi kỹ thuật bằng Regex (E-204, ALM-03, PCB-D02...)
- Dual-retrieval: Regex Error-Code Boost kết hợp Dense Cosine Search
- Ngưỡng lọc tương đồng SIMILARITY_THRESHOLD = 0.65 từ chối câu hỏi ngoài phạm vi
- Hỗ trợ truy hồi bất đồng bộ aretrieve()
"""
import hashlib
import math
from pathlib import Path
import re
from typing import List
from uuid import uuid4

import pytest

from app.core.config import settings
from app.rag.embeddings import ChromaEmbeddingFunction
from app.rag.retriever import SOPRetriever, extract_error_codes
from app.rag.vector_store import VectorStoreService
from app.utils.chunker import chunk_document
from app.utils.pdf_parser import parse_pdf_document


SOPS_DIR = Path(settings.PROJECT_ROOT) / "data" / "sops"
if not SOPS_DIR.exists():
    SOPS_DIR = Path(settings.BACKEND_DIR) / "data" / "sops"


def _local_hash_encode(texts: List[str]) -> List[List[float]]:
    vectors: List[List[float]] = []
    for text in texts:
        vec = [0.0] * 2048
        tokens = set(re.findall(r"[a-z0-9\-_]+", text.lower()))
        for tok in tokens:
            digest = hashlib.sha256(tok.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % 2048
            weight = 2.0 if ("-" in tok or any(ch.isdigit() for ch in tok)) else 1.0
            vec[idx] += weight
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        vectors.append([v / norm for v in vec])
    return vectors


def _build_seeded_store(tmp_path: Path) -> VectorStoreService:
    ef = ChromaEmbeddingFunction(
        encode_fn=_local_hash_encode,
        model_name="test-hash-2048d",
    )
    vs = VectorStoreService(
        persist_dir=tmp_path / "chromadb",
        collection_name=f"test_ret_{uuid4().hex[:8]}",
        embedding_function=ef,
    )
    samples = [
        ("doc-feeder-004", "SOP-FEEDER-004-VN", "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf"),
        ("doc-pcb-005", "SOP-PCB-005-VN", "SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf"),
    ]
    for doc_id, doc_code, filename in samples:
        parsed = parse_pdf_document(SOPS_DIR / filename)
        chunks = chunk_document(parsed)
        vs.upsert_chunks(doc_id=doc_id, chunks=chunks, source_file=filename, doc_code=doc_code)
    return vs


def test_extract_error_codes_regex():
    """Regex trích xuất chính xác và chuẩn hóa các mã lỗi / mã khuyết tật công nghiệp."""
    codes = extract_error_codes(
        "Máy gắp báo lỗi e-204 kẹt feeder, sau đó máy PCB báo pcb-d02 và ALM-03 lặp lại E-204"
    )
    assert codes == ["E-204", "PCB-D02", "ALM-03"]
    assert extract_error_codes("Cách thay nhớt xe máy Honda Wave?") == []


def test_dual_retrieval_exact_error_code_boost(tmp_path: Path):
    """Truy vấn tiếng Việt chứa mã lỗi E-204 tìm đúng chunk trang 1 SOP_FEEDER_004 với boost >= 0.85."""
    vs = _build_seeded_store(tmp_path)
    retriever = SOPRetriever(vector_store=vs, similarity_threshold=0.65)

    res = retriever.retrieve("Máy báo lỗi E-204 kẹt cuộn xử lý thế nào?", top_k=3)
    assert res["retrieval_mode"] == "dual_hybrid"
    assert res["detected_error_codes"] == ["E-204"]
    assert res["is_out_of_domain"] is False
    assert res["top_score"] >= 0.85
    assert len(res["chunks"]) >= 1

    top = res["chunks"][0]
    assert "E-204" in top["content"]
    assert top["metadata"]["source_file"] == "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf"
    assert top["metadata"]["page_num"] == 1
    assert top["match_type"] in {"hybrid_exact", "exact_error_code"}


def test_dual_retrieval_pcb_defect_code(tmp_path: Path):
    """Truy vấn chứa mã khuyết tật PCB-D02 trả về đúng chunk bảng kiểm định SOP_PCB_005."""
    vs = _build_seeded_store(tmp_path)
    retriever = SOPRetriever(vector_store=vs, similarity_threshold=0.65)

    res = retriever.retrieve("Tiêu chuẩn xử lý lỗi PCB-D02?", top_k=3)
    assert res["detected_error_codes"] == ["PCB-D02"]
    assert res["is_out_of_domain"] is False
    top = res["chunks"][0]
    assert "PCB-D02" in top["content"]
    assert top["metadata"]["source_file"] == "SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf"


def test_out_of_domain_query_rejected_below_threshold(tmp_path: Path):
    """Câu hỏi ngoài phạm vi nhà máy có score < 0.65 -> bị từ chối với is_out_of_domain=True."""
    vs = _build_seeded_store(tmp_path)
    retriever = SOPRetriever(vector_store=vs, similarity_threshold=0.65)

    res = retriever.retrieve("Cách thay nhớt xe máy Honda Wave?", top_k=5)
    assert res["retrieval_mode"] == "semantic"
    assert res["detected_error_codes"] == []
    assert res["top_score"] < 0.65
    assert res["chunks"] == []
    assert res["is_out_of_domain"] is True


@pytest.mark.asyncio
async def test_aretrieve_async_wrapper(tmp_path: Path):
    """aretrieve() thực thi truy hồi trong threadpool trả về kết quả đồng nhất với retrieve()."""
    vs = _build_seeded_store(tmp_path)
    retriever = SOPRetriever(vector_store=vs, similarity_threshold=0.65)

    res = await retriever.aretrieve("Xử lý mã lỗi E-204", top_k=2)
    assert res["is_out_of_domain"] is False
    assert "E-204" in res["chunks"][0]["content"]
