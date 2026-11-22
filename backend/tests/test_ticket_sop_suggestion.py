"""
Unit & Integration test suite cho Milestone 3.2 - Phần 2 (AI SOP Suggestion cho Incident Tickets):
- Kỹ sư tạo phiếu sự cố với mã lỗi E-204 tự động được điền suggested_sop_id, suggested_page, suggested_snippet
- Endpoint preview GET /api/v1/incident_tickets/suggest-sop trả về gợi ý đúng hoặc None khi ngoài phạm vi
"""
import hashlib
import math
from pathlib import Path
import re
from typing import List
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import delete

import app.services.ticket_service as ticket_service_module
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.sop_document import IngestionStatus, SOPDocument
from app.rag.embeddings import ChromaEmbeddingFunction
from app.rag.retriever import SOPRetriever
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


async def _setup_sop_and_retriever(tmp_path: Path):
    """Tạo bản ghi SOPDocument thật trong CSDL và lập chỉ mục vào ChromaDB test cô lập."""
    filename = "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf"
    doc_code = f"SOP-SUGGEST-{uuid4().hex[:6]}"
    async with AsyncSessionLocal() as db:
        sop = SOPDocument(
            document_code=doc_code,
            title="Feeder Tape & Reel Troubleshooting",
            file_name=filename,
            file_path=f"data/sops/{filename}",
            file_hash=f"suggest-hash-{uuid4().hex}",
            file_size=1024,
            version="1.0",
            page_count=2,
            chunk_count=0,
            ingestion_status=IngestionStatus.COMPLETED,
        )
        db.add(sop)
        await db.commit()
        await db.refresh(sop)

    ef = ChromaEmbeddingFunction(
        encode_fn=_local_hash_encode,
        model_name="test-hash-2048d",
    )
    vs = VectorStoreService(
        persist_dir=tmp_path / "chromadb",
        collection_name=f"test_suggest_{uuid4().hex[:8]}",
        embedding_function=ef,
    )
    parsed = parse_pdf_document(SOPS_DIR / filename)
    chunks = chunk_document(parsed)
    vs.upsert_chunks(doc_id=sop.id, chunks=chunks, source_file=filename, doc_code=sop.document_code)
    return sop, SOPRetriever(vector_store=vs, similarity_threshold=0.65)


async def _cleanup(ticket_id: str | None, sop_id: str, admin_token: str, client: AsyncClient):
    if ticket_id:
        await client.delete(
            f"/api/v1/incident_tickets/{ticket_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    async with AsyncSessionLocal() as db:
        await db.execute(delete(SOPDocument).where(SOPDocument.id == sop_id))
        await db.commit()


async def _get_token(client: AsyncClient, username: str, password: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_ticket_auto_suggests_matching_sop_for_e204(tmp_path: Path, monkeypatch):
    """GATE TEST 3.2: Tạo phiếu sự cố E-204 tự động gắn suggested_sop_id và suggested_page đúng."""
    sop, retriever = await _setup_sop_and_retriever(tmp_path)
    monkeypatch.setattr(ticket_service_module, "get_retriever", lambda: retriever)

    created_ticket_id = None
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        eng_token = await _get_token(client, "engineer", "Engineer@2026")
        admin_token = await _get_token(client, "admin", "Admin@2026")

        try:
            mac_resp = await client.get(
                "/api/v1/machines",
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            machine_id = mac_resp.json()[0]["id"]

            resp = await client.post(
                "/api/v1/incident_tickets",
                json={
                    "machine_id": machine_id,
                    "error_code": "E-204",
                    "description": "Lỗi kẹt đầu hút linh kiện feeder jam",
                    "priority": "HIGH",
                },
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert resp.status_code == 201
            data = resp.json()
            created_ticket_id = data["id"]

            assert data["suggested_sop_id"] == sop.id
            assert data["suggested_page"] == 1
            assert data["suggested_snippet"] is not None
            assert "E-204" in data["suggested_snippet"]
        finally:
            await _cleanup(created_ticket_id, sop.id, admin_token, client)


@pytest.mark.asyncio
async def test_suggest_sop_preview_endpoint_found_and_not_found(tmp_path: Path, monkeypatch):
    """GET /api/v1/incident_tickets/suggest-sop trả về gợi ý hợp lệ hoặc None nếu ngoài phạm vi."""
    sop, retriever = await _setup_sop_and_retriever(tmp_path)
    monkeypatch.setattr(ticket_service_module, "get_retriever", lambda: retriever)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        eng_token = await _get_token(client, "engineer", "Engineer@2026")
        admin_token = await _get_token(client, "admin", "Admin@2026")

        try:
            resp_ok = await client.get(
                "/api/v1/incident_tickets/suggest-sop",
                params={"error_code": "E-204", "description": "feeder jam"},
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert resp_ok.status_code == 200
            body_ok = resp_ok.json()
            assert body_ok["found"] is True
            assert body_ok["suggestion"]["suggested_sop_id"] == sop.id
            assert body_ok["suggestion"]["suggested_page"] == 1

            resp_none = await client.get(
                "/api/v1/incident_tickets/suggest-sop",
                params={"error_code": "", "description": "cách thay nhớt xe máy Honda Wave"},
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert resp_none.status_code == 200
            body_none = resp_none.json()
            assert body_none["found"] is False
            assert body_none["suggestion"] is None
        finally:
            await _cleanup(None, sop.id, admin_token, client)
