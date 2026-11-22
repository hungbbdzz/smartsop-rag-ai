"""
Unit test suite cho Milestone 2.2 (Gate Test 2.2):
- Pipeline nạp tri thức PDF -> Table-Aware Chunks -> ChromaDB Vector Store -> SQL sop_chunks
- Truy vấn tương đồng Cosine tìm đúng mã lỗi kỹ thuật (E-204 / feeder jam)
- Tính Idempotent khi re-ingest, đồng bộ xóa vector khi xóa SOP, và xử lý nạp đồng thời
"""
import asyncio
import hashlib
import math
from pathlib import Path
import re
from typing import List
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import delete, select

import app.rag.ingestion as ingestion_module
import app.rag.vector_store as vector_store_module
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.sop_chunk import SOPChunk
from app.models.sop_document import IngestionStatus, SOPDocument
from app.rag.embeddings import ChromaEmbeddingFunction
from app.rag.ingestion import ingest_sop_document
from app.rag.vector_store import VectorStoreService


SOPS_DIR = Path(settings.PROJECT_ROOT) / "data" / "sops"
if not SOPS_DIR.exists():
    SOPS_DIR = Path(settings.BACKEND_DIR) / "data" / "sops"


def deterministic_hash_encode(texts: List[str]) -> List[List[float]]:
    """
    Hàm nhúng tất định 2048 chiều (chuẩn hóa L2) dùng trong unit test để kiểm thử
    end-to-end ChromaDB PersistentClient nhanh chóng mà không cần tải trọng số 2.2GB.
    """
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


def make_test_vector_store(tmp_path: Path) -> VectorStoreService:
    """Tạo VectorStoreService cô lập trên thư mục tạm cho từng ca kiểm thử."""
    ef = ChromaEmbeddingFunction(
        encode_fn=deterministic_hash_encode,
        model_name="test-hash-128d",
    )
    return VectorStoreService(
        persist_dir=tmp_path / "chromadb",
        collection_name=f"test_sops_{uuid4().hex[:8]}",
        embedding_function=ef,
    )


async def _create_sop_record(pdf_filename: str, document_code: str, title: str) -> SOPDocument:
    """Tạo bản ghi SOPDocument tạm trong CSDL trỏ tới file PDF mẫu."""
    async with AsyncSessionLocal() as db:
        doc = SOPDocument(
            document_code=document_code,
            title=title,
            file_name=pdf_filename,
            file_path=f"data/sops/{pdf_filename}",
            file_hash=f"test-hash-{uuid4().hex}",
            file_size=1024,
            version="1.0",
            page_count=0,
            chunk_count=0,
            ingestion_status=IngestionStatus.PENDING,
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        return doc


async def _cleanup_sop_record(document_id: str) -> None:
    """Dọn dẹp bản ghi SOPDocument và SOPChunk sau khi chạy test."""
    async with AsyncSessionLocal() as db:
        await db.execute(delete(SOPChunk).where(SOPChunk.document_id == document_id))
        await db.execute(delete(SOPDocument).where(SOPDocument.id == document_id))
        await db.commit()


async def _get_token(client: AsyncClient, username: str, password: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_ingest_sop_document_end_to_end(tmp_path: Path):
    """GATE TEST 2.2: Nạp PDF thành công, số vector ChromaDB khớp 100% với bảng sop_chunks và ID tất định."""
    vs = make_test_vector_store(tmp_path)
    doc = await _create_sop_record(
        pdf_filename="SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf",
        document_code=f"TEST-FEEDER-{uuid4().hex[:6]}",
        title="Feeder Tape & Reel Setup Test",
    )

    try:
        summary = await ingest_sop_document(doc.id, vector_store=vs)
        assert summary["status"] == IngestionStatus.COMPLETED.value
        assert summary["chunk_count"] > 0
        assert vs.count_by_doc_id(doc.id) == summary["chunk_count"]

        async with AsyncSessionLocal() as db:
            db_doc = (await db.execute(select(SOPDocument).where(SOPDocument.id == doc.id))).scalar_one()
            assert db_doc.ingestion_status == IngestionStatus.COMPLETED
            assert db_doc.chunk_count == summary["chunk_count"]
            assert db_doc.page_count == 2

            db_chunks = (
                await db.execute(select(SOPChunk).where(SOPChunk.document_id == doc.id))
            ).scalars().all()
            assert len(db_chunks) == summary["chunk_count"]
            for ch in db_chunks:
                expected_id = f"{doc.id}:{ch.page_num}:{ch.chunk_index}"
                assert ch.chroma_id == expected_id
    finally:
        await _cleanup_sop_record(doc.id)


@pytest.mark.asyncio
async def test_vector_query_retrieves_e204_feeder_jam(tmp_path: Path):
    """GATE TEST 2.2: Truy vấn 'E-204 feeder jam pickup reject' trả về đúng chunk trang 1 chứa mã lỗi E-204."""
    vs = make_test_vector_store(tmp_path)
    doc = await _create_sop_record(
        pdf_filename="SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf",
        document_code=f"TEST-QUERY-{uuid4().hex[:6]}",
        title="Feeder Query Test",
    )

    try:
        await ingest_sop_document(doc.id, vector_store=vs)
        results = vs.query("E-204 feeder jam pickup reject", top_k=3)
        assert len(results) >= 1

        top = results[0]
        assert "E-204" in top["content"]
        assert top["metadata"]["doc_id"] == doc.id
        assert top["metadata"]["page_num"] == 1
        assert top["metadata"]["source_file"] == "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf"
    finally:
        await _cleanup_sop_record(doc.id)


@pytest.mark.asyncio
async def test_reingest_is_idempotent(tmp_path: Path):
    """GATE TEST 2.2: Re-ingest cùng một tài liệu giữ nguyên số vector và bản ghi DB, không trùng lặp."""
    vs = make_test_vector_store(tmp_path)
    doc = await _create_sop_record(
        pdf_filename="SOP_PCB_005_Bare_Board_Cleanliness_And_Inspection.pdf",
        document_code=f"TEST-IDEMP-{uuid4().hex[:6]}",
        title="Idempotency Test",
    )

    try:
        res1 = await ingest_sop_document(doc.id, vector_store=vs)
        res2 = await ingest_sop_document(doc.id, vector_store=vs)

        assert res1["chunk_count"] == res2["chunk_count"]
        assert vs.count_by_doc_id(doc.id) == res1["chunk_count"]
        assert vs.count() == res1["chunk_count"]

        async with AsyncSessionLocal() as db:
            db_chunks = (
                await db.execute(select(SOPChunk).where(SOPChunk.document_id == doc.id))
            ).scalars().all()
            assert len(db_chunks) == res1["chunk_count"]
    finally:
        await _cleanup_sop_record(doc.id)


@pytest.mark.asyncio
async def test_delete_sop_cleans_vectors_and_db_chunks(tmp_path: Path, monkeypatch):
    """GATE TEST 2.2: Admin xóa SOP qua REST API phải xóa sạch 100% vector trong ChromaDB và bảng sop_chunks."""
    vs = make_test_vector_store(tmp_path)
    monkeypatch.setattr(ingestion_module, "get_vector_store", lambda: vs)
    monkeypatch.setattr(vector_store_module, "get_vector_store", lambda: vs)

    doc = await _create_sop_record(
        pdf_filename="SOP_AOI_003_Automated_Optical_Inspection_Standards.pdf",
        document_code=f"TEST-DELVEC-{uuid4().hex[:6]}",
        title="Delete Sync Vector Test",
    )

    try:
        summary = await ingest_sop_document(doc.id, vector_store=vs)
        assert vs.count_by_doc_id(doc.id) == summary["chunk_count"] > 0

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            admin_token = await _get_token(client, "admin", "Admin@2026")
            del_resp = await client.delete(
                f"/api/v1/sop_documents/{doc.id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert del_resp.status_code == 200

        assert vs.count_by_doc_id(doc.id) == 0
        async with AsyncSessionLocal() as db:
            remaining_chunks = (
                await db.execute(select(SOPChunk).where(SOPChunk.document_id == doc.id))
            ).scalars().all()
            assert remaining_chunks == []
    finally:
        await _cleanup_sop_record(doc.id)


@pytest.mark.asyncio
async def test_concurrent_ingestion_two_pdfs_no_race_condition(tmp_path: Path):
    """GATE TEST 2.2: Nạp đồng thời 2 file PDF bằng asyncio.gather đều hoàn thành trơn tru không race condition."""
    vs = make_test_vector_store(tmp_path)
    doc1 = await _create_sop_record(
        pdf_filename="SOP_SMT_001_Pick_And_Place_Machine_Troubleshooting.pdf",
        document_code=f"TEST-CONC1-{uuid4().hex[:6]}",
        title="Concurrent SMT 001",
    )
    doc2 = await _create_sop_record(
        pdf_filename="SOP_REFLOW_002_Reflow_Soldering_Defects_Remedies.pdf",
        document_code=f"TEST-CONC2-{uuid4().hex[:6]}",
        title="Concurrent Reflow 002",
    )

    try:
        res1, res2 = await asyncio.gather(
            ingest_sop_document(doc1.id, vector_store=vs),
            ingest_sop_document(doc2.id, vector_store=vs),
        )

        assert res1["status"] == IngestionStatus.COMPLETED.value
        assert res2["status"] == IngestionStatus.COMPLETED.value
        assert vs.count_by_doc_id(doc1.id) == res1["chunk_count"]
        assert vs.count_by_doc_id(doc2.id) == res2["chunk_count"]
        assert vs.count() == res1["chunk_count"] + res2["chunk_count"]

        async with AsyncSessionLocal() as db:
            c1 = (await db.execute(select(SOPChunk).where(SOPChunk.document_id == doc1.id))).scalars().all()
            c2 = (await db.execute(select(SOPChunk).where(SOPChunk.document_id == doc2.id))).scalars().all()
            assert len(c1) == res1["chunk_count"]
            assert len(c2) == res2["chunk_count"]
    finally:
        await _cleanup_sop_record(doc1.id)
        await _cleanup_sop_record(doc2.id)
