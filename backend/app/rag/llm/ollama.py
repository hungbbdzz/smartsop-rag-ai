import json
import logging
from typing import Any, AsyncIterator, Dict, Optional

import httpx

from app.core.config import settings
from app.rag.llm.base import BaseLLMProvider

logger = logging.getLogger("smartsop.rag.llm.ollama")


class OllamaProvider(BaseLLMProvider):
    """
    Provider kết nối Ollama Local API phục vụ kịch bản vận hành nội bộ không Internet.
    Hỗ trợ gọi chuẩn `/api/chat` (non-stream & NDJSON stream) và `/api/tags` cho health check.
    """

    provider_name: str = "ollama"

    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: float = 120.0,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        super().__init__(model_name=model_name or settings.OLLAMA_MODEL)
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.timeout = timeout
        self._transport = transport

    def _make_client(self) -> httpx.AsyncClient:
        kwargs: Dict[str, Any] = {"timeout": self.timeout}
        if self._transport is not None:
            kwargs["transport"] = self._transport
        return httpx.AsyncClient(**kwargs)

    def _build_payload(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        stream: bool,
    ) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": stream,
            "options": {"temperature": temperature},
        }

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> str:
        payload = self._build_payload(system_prompt, user_prompt, temperature, stream=False)
        async with self._make_client() as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
        return ((data.get("message") or {}).get("content") or "").strip()

    async def astream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> AsyncIterator[str]:
        payload = self._build_payload(system_prompt, user_prompt, temperature, stream=True)
        async with self._make_client() as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line or not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        logger.warning(f"Bỏ qua dòng NDJSON không hợp lệ từ Ollama: {line!r}")
                        continue

                    token = (data.get("message") or {}).get("content")
                    if token:
                        yield token
                    if data.get("done"):
                        break

    async def health_check(self) -> Dict[str, Any]:
        try:
            async with self._make_client() as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                data = resp.json()
            available_models = [m.get("name", "") for m in (data.get("models") or [])]
            has_model = any(
                m == self.model_name or m.startswith(f"{self.model_name}:")
                for m in available_models
            )
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "base_url": self.base_url,
                "status": "ok" if has_model else "model_missing",
                "available_models": available_models,
            }
        except Exception as exc:
            return {
                "provider": self.provider_name,
                "model": self.model_name,
                "base_url": self.base_url,
                "status": "unreachable",
                "detail": str(exc),
            }
