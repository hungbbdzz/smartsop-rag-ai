"""
Unit & Integration test suite cho Milestone 3.2 - Phần 1 (SSE Streaming Chat):
- Yêu cầu xác thực Bearer Token tại POST /api/v1/chat/query
- SSE stream trả về tuần tự token, citation (đối soát chunk thực tế), done và lưu chat_audit_logs
- Câu hỏi ngoài phạm vi từ chối ngay không gọi LLM (is_refused=True, citations=[])
- 3 người dùng gửi câu hỏi song song không nghẽn luồng
"""
import asyncio
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any, AsyncIterator, Dict, List
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import delete, select

import app.rag.streaming as streaming_module
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.chat_audit_log import ChatAuditLog
from app.rag.embeddings import ChromaEmbeddingFunction
from app.rag.llm.base import BaseLLMProvider
from app.rag.prompt_engine import REFUSAL_MESSAGE
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


def _make_seeded_retriever(tmp_path: Path) -> SOPRetriever:
    ef = ChromaEmbeddingFunction(
        encode_fn=_local_hash_encode,
        model_name="test-hash-2048d",
    )
    vs = VectorStoreService(
        persist_dir=tmp_path / "chromadb",
        collection_name=f"test_chat_{uuid4().hex[:8]}",
        embedding_function=ef,
    )
    parsed = parse_pdf_document(SOPS_DIR / "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf")
    chunks = chunk_document(parsed)
    vs.upsert_chunks(
        doc_id="doc-feeder-004",
        chunks=chunks,
        source_file="SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf",
        doc_code="SOP-FEEDER-004-VN",
    )
    return SOPRetriever(vector_store=vs, similarity_threshold=0.65)


class _FakeStreamingLLM(BaseLLMProvider):
    provider_name = "fake"

    def __init__(self, tokens: List[str]) -> None:
        super().__init__(model_name="fake-stream-1.0")
        self._tokens = tokens

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        return "".join(self._tokens)

    async def astream(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.1
    ) -> AsyncIterator[str]:
        for tok in self._tokens:
            await asyncio.sleep(0)
            yield tok


class _SpyNeverCallLLM(BaseLLMProvider):
    provider_name = "spy"

    def __init__(self) -> None:
        super().__init__(model_name="spy-never-call")

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        raise AssertionError("LLM không được phép được gọi cho câu hỏi ngoài phạm vi!")

    async def astream(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.1
    ) -> AsyncIterator[str]:
        raise AssertionError("LLM không được phép được gọi cho câu hỏi ngoài phạm vi!")
        if False:  # pragma: no cover
            yield ""


def _parse_sse_events(body_text: str) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for block in body_text.strip().split("\n\n"):
        for line in block.splitlines():
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))
    return events


async def _get_token(client: AsyncClient, username: str, password: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


async def _cleanup_audit_logs(log_ids: List[str]) -> None:
    if not log_ids:
        return
    async with AsyncSessionLocal() as db:
        await db.execute(delete(ChatAuditLog).where(ChatAuditLog.id.in_(log_ids)))
        await db.commit()


@pytest.mark.asyncio
async def test_chat_query_requires_authentication():
    """POST /api/v1/chat/query không đính kèm Bearer token -> HTTP 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/chat/query",
            json={"question": "Lỗi E-204 xử lý thế nào?"},
        )
        assert resp.status_code in [401, 403]


@pytest.mark.asyncio
async def test_chat_query_sse_in_domain_e204_streams_tokens_citations_and_logs(tmp_path: Path, monkeypatch):
    """GATE TEST 3.2: Truyền SSE tuần tự token -> citation (E-204 trang 1) -> done và ghi chat_audit_logs."""
    retriever = _make_seeded_retriever(tmp_path)
    fake_llm = _FakeStreamingLLM([
        "📌 Mã lỗi E-204 (Feeder Jam). ",
        "🛠️ Nhấn Pause và gỡ màng băng bị đứt ",
        "[SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf - Trang 1].",
    ])
    monkeypatch.setattr(streaming_module, "get_retriever", lambda: retriever)
    monkeypatch.setattr(streaming_module, "get_llm_provider", lambda: fake_llm)

    created_log_ids: List[str] = []
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            op_token = await _get_token(client, "operator", "Operator@2026")
            resp = await client.post(
                "/api/v1/chat/query",
                json={"question": "Máy báo lỗi E-204 xử lý thế nào?"},
                headers={"Authorization": f"Bearer {op_token}"},
            )
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers["content-type"]

            events = _parse_sse_events(resp.text)
            token_events = [e for e in events if e["type"] == "token"]
            citation_events = [e for e in events if e["type"] == "citation"]
            done_events = [e for e in events if e["type"] == "done"]

            assert len(token_events) == 3
            assert "E-204" in "".join(e["content"] for e in token_events)

            assert len(citation_events) == 1
            assert citation_events[0]["doc_id"] == "doc-feeder-004"
            assert citation_events[0]["file"] == "SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf"
            assert citation_events[0]["page"] == 1

            assert len(done_events) == 1
            done = done_events[0]
            assert done["is_refused"] is False
            assert done["ttft_ms"] is not None
            assert done["audit_log_id"] is not None
            created_log_ids.append(done["audit_log_id"])

            async with AsyncSessionLocal() as db:
                log_row = (
                    await db.execute(select(ChatAuditLog).where(ChatAuditLog.id == done["audit_log_id"]))
                ).scalar_one()
                assert log_row.is_refused is False
                assert log_row.cited_doc_ids == ["doc-feeder-004"]
                assert log_row.cited_pages == [1]
                assert log_row.ttft_ms is not None
    finally:
        await _cleanup_audit_logs(created_log_ids)


@pytest.mark.asyncio
async def test_chat_query_out_of_domain_refuses_without_calling_llm(tmp_path: Path, monkeypatch):
    """Câu hỏi ngoài phạm vi từ chối chuẩn ngay từ Retriever, không gọi LLM, citations rỗng."""
    retriever = _make_seeded_retriever(tmp_path)
    spy_llm = _SpyNeverCallLLM()
    monkeypatch.setattr(streaming_module, "get_retriever", lambda: retriever)
    monkeypatch.setattr(streaming_module, "get_llm_provider", lambda: spy_llm)

    created_log_ids: List[str] = []
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            op_token = await _get_token(client, "operator", "Operator@2026")
            resp = await client.post(
                "/api/v1/chat/query",
                json={"question": "Cách thay nhớt xe máy Honda Wave?"},
                headers={"Authorization": f"Bearer {op_token}"},
            )
            assert resp.status_code == 200
            events = _parse_sse_events(resp.text)

            token_events = [e for e in events if e["type"] == "token"]
            citation_events = [e for e in events if e["type"] == "citation"]
            done_events = [e for e in events if e["type"] == "done"]

            assert token_events == [{"type": "token", "content": REFUSAL_MESSAGE}]
            assert citation_events == []
            assert len(done_events) == 1
            assert done_events[0]["is_refused"] is True
            created_log_ids.append(done_events[0]["audit_log_id"])
    finally:
        await _cleanup_audit_logs(created_log_ids)


@pytest.mark.asyncio
async def test_chat_query_three_concurrent_users_no_blocking(tmp_path: Path, monkeypatch):
    """GATE TEST 3.2: 3 người dùng cùng gửi câu hỏi song song đều nhận phản hồi SSE mượt mà."""
    retriever = _make_seeded_retriever(tmp_path)
    fake_llm = _FakeStreamingLLM([
        "Xử lý E-204 ",
        "[SOP_FEEDER_004_Tape_And_Reel_Setup_Guide.pdf - Trang 1]",
    ])
    monkeypatch.setattr(streaming_module, "get_retriever", lambda: retriever)
    monkeypatch.setattr(streaming_module, "get_llm_provider", lambda: fake_llm)

    created_log_ids: List[str] = []
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            op_token = await _get_token(client, "operator", "Operator@2026")
            eng_token = await _get_token(client, "engineer", "Engineer@2026")
            mgr_token = await _get_token(client, "manager", "Manager@2026")

            async def _send(tok: str, q: str):
                return await client.post(
                    "/api/v1/chat/query",
                    json={"question": q},
                    headers={"Authorization": f"Bearer {tok}"},
                )

            responses = await asyncio.gather(
                _send(op_token, "Lỗi E-204 xử lý sao?"),
                _send(eng_token, "Feeder kẹt mã E-204"),
                _send(mgr_token, "Khắc phục lỗi E-204"),
            )

            for r in responses:
                assert r.status_code == 200
                events = _parse_sse_events(r.text)
                done = [e for e in events if e["type"] == "done"]
                assert len(done) == 1
                assert done[0]["is_refused"] is False
                created_log_ids.append(done[0]["audit_log_id"])
    finally:
        await _cleanup_audit_logs(created_log_ids)
