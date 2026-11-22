"""
Unit test suite cho Milestone 3.1 - Phần 3 (Dual-Provider LLM Abstraction):
- Factory lựa chọn GeminiProvider / OllamaProvider và từ chối provider không hợp lệ
- GeminiProvider kiểm tra thiếu GEMINI_API_KEY, generate() & astream() qua mock async client
- OllamaProvider generate(), NDJSON astream() & health_check() qua httpx.MockTransport
"""
import json
from types import SimpleNamespace

import httpx
import pytest

from app.rag.llm import (
    GeminiProvider,
    OllamaProvider,
    create_llm_provider,
    get_llm_provider,
)


def test_factory_selects_gemini_or_ollama_and_rejects_invalid(monkeypatch):
    """Factory tạo đúng provider theo tham số hoặc settings.LLM_PROVIDER và chặn tên sai."""
    gem = create_llm_provider("gemini", api_key="fake-key")
    assert isinstance(gem, GeminiProvider)
    assert gem.provider_name == "gemini"

    oll = create_llm_provider("OLLAMA", base_url="http://localhost:11434", model_name="qwen2.5:7b")
    assert isinstance(oll, OllamaProvider)
    assert oll.provider_name == "ollama"
    assert oll.model_name == "qwen2.5:7b"

    monkeypatch.setattr("app.rag.llm.factory.settings.LLM_PROVIDER", "ollama")
    assert isinstance(get_llm_provider(), OllamaProvider)

    with pytest.raises(ValueError, match="không được hỗ trợ"):
        create_llm_provider("openai-unknown")


@pytest.mark.asyncio
async def test_gemini_provider_requires_api_key():
    """GeminiProvider ném ValueError rõ ràng khi gọi generate/astream mà thiếu GEMINI_API_KEY."""
    provider = GeminiProvider(api_key="", model_name="gemini-1.5-flash")

    health = await provider.health_check()
    assert health["status"] == "unconfigured"
    assert health["configured"] is False

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        await provider.generate("system", "user")

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        async for _ in provider.astream("system", "user"):
            pass


@pytest.mark.asyncio
async def test_gemini_provider_generate_and_stream_with_mock_client():
    """GeminiProvider.generate() và .astream() đọc đúng phản hồi từ client.aio.models."""
    captured_calls = []

    class _FakeAsyncModels:
        async def generate_content(self, *, model, contents, config):
            captured_calls.append(("generate", model, contents, config.system_instruction))
            return SimpleNamespace(text="  Quy trình xử lý lỗi E-204  ")

        async def generate_content_stream(self, *, model, contents, config):
            captured_calls.append(("stream", model, contents, config.system_instruction))

            async def _gen():
                for piece in ["Bước 1: ", "Nhấn Pause", "", " và gỡ băng kẹt."]:
                    yield SimpleNamespace(text=piece)

            return _gen()

    fake_client = SimpleNamespace(aio=SimpleNamespace(models=_FakeAsyncModels()))
    provider = GeminiProvider(model_name="gemini-1.5-flash", client=fake_client)

    full_text = await provider.generate("SYS_GUARD", "Lỗi E-204?", temperature=0.0)
    assert full_text == "Quy trình xử lý lỗi E-204"

    tokens = [tok async for tok in provider.astream("SYS_GUARD", "Lỗi E-204?")]
    assert tokens == ["Bước 1: ", "Nhấn Pause", " và gỡ băng kẹt."]
    assert len(captured_calls) == 2
    assert captured_calls[0][1] == "gemini-1.5-flash"
    assert captured_calls[1][3] == "SYS_GUARD"


@pytest.mark.asyncio
async def test_ollama_provider_generate_and_stream_with_mock_transport():
    """OllamaProvider hỗ trợ offline generate(), phân giải NDJSON stream và kiểm tra /api/tags."""
    def _handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(
                200,
                json={"models": [{"name": "qwen2.5:7b"}, {"name": "llama3:8b"}]},
            )
        if request.url.path == "/api/chat":
            body = json.loads(request.content.decode("utf-8"))
            assert body["model"] == "qwen2.5:7b"
            assert body["messages"][0]["role"] == "system"
            if body.get("stream") is False:
                return httpx.Response(
                    200,
                    json={"message": {"role": "assistant", "content": "Đã kiểm tra lò Reflow."}},
                )
            ndjson_lines = "\n".join([
                json.dumps({"message": {"content": "Kiểm tra "}, "done": False}),
                json.dumps({"message": {"content": "nguồn khí"}, "done": False}),
                json.dumps({"message": {"content": ""}, "done": True}),
            ])
            return httpx.Response(200, content=ndjson_lines.encode("utf-8"))
        return httpx.Response(404)

    transport = httpx.MockTransport(_handler)
    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model_name="qwen2.5:7b",
        transport=transport,
    )

    health = await provider.health_check()
    assert health["status"] == "ok"
    assert "qwen2.5:7b" in health["available_models"]

    result = await provider.generate("SYS", "Nhiệt độ Reflow?")
    assert result == "Đã kiểm tra lò Reflow."

    streamed = [tok async for tok in provider.astream("SYS", "Nhiệt độ Reflow?")]
    assert streamed == ["Kiểm tra ", "nguồn khí"]
