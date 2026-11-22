import inspect
import logging
from typing import Any, AsyncIterator, Dict, Optional

from google import genai
from google.genai import types

from app.core.config import settings
from app.rag.llm.base import BaseLLMProvider

logger = logging.getLogger("smartsop.rag.llm.gemini")


class GeminiProvider(BaseLLMProvider):
    """
    Provider kết nối Google Gemini API qua SDK `google-genai`.
    Sử dụng `client.aio.models` cho xử lý bất đồng bộ và streaming TTFT thấp.
    """

    provider_name: str = "gemini"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        super().__init__(model_name=model_name or settings.GEMINI_MODEL)
        self.api_key = settings.GEMINI_API_KEY if api_key is None else api_key
        self._client = client

    def _get_client(self) -> Any:
        if self._client is None:
            if not self.api_key or not self.api_key.strip():
                raise ValueError(
                    "GEMINI_API_KEY chưa được cấu hình. Vui lòng thiết lập biến môi trường "
                    "GEMINI_API_KEY hoặc chuyển sang LLM_PROVIDER=ollama."
                )
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _build_config(
        self,
        system_prompt: str,
        temperature: float,
    ) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> str:
        client = self._get_client()
        config = self._build_config(system_prompt, temperature)
        response = await client.aio.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=config,
        )
        return (getattr(response, "text", None) or "").strip()

    async def astream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> AsyncIterator[str]:
        client = self._get_client()
        config = self._build_config(system_prompt, temperature)
        stream_or_coro = client.aio.models.generate_content_stream(
            model=self.model_name,
            contents=user_prompt,
            config=config,
        )
        if inspect.isawaitable(stream_or_coro):
            stream_or_coro = await stream_or_coro

        async for chunk in stream_or_coro:
            text = getattr(chunk, "text", None)
            if text:
                yield text

    async def health_check(self) -> Dict[str, Any]:
        configured = bool(self._client is not None or (self.api_key and self.api_key.strip()))
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "status": "configured" if configured else "unconfigured",
            "configured": configured,
        }
