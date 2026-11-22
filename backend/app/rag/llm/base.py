from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict


class BaseLLMProvider(ABC):
    """
    Interface trừu tượng chuẩn hóa các mô hình ngôn ngữ lớn (Dual-Provider LLM):
    - Cho phép chuyển đổi linh hoạt giữa Cloud API (Gemini) và Offline Local (Ollama).
    """

    provider_name: str = "base"

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> str:
        """Sinh toàn bộ câu trả lời (non-streaming)."""
        raise NotImplementedError

    @abstractmethod
    async def astream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> AsyncIterator[str]:
        """Sinh từng đoạn token văn bản bất đồng bộ phục vụ SSE streaming."""
        raise NotImplementedError
        if False:  # pragma: no cover
            yield ""

    async def health_check(self) -> Dict[str, Any]:
        """Kiểm tra trạng thái sẵn sàng của provider."""
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "status": "unknown",
        }
