from typing import Any, Optional

from app.core.config import settings
from app.rag.llm.base import BaseLLMProvider
from app.rag.llm.gemini import GeminiProvider
from app.rag.llm.ollama import OllamaProvider


def create_llm_provider(
    provider_name: Optional[str] = None,
    **kwargs: Any,
) -> BaseLLMProvider:
    """
    Factory khởi tạo LLM Provider theo tên hoặc cấu hình `settings.LLM_PROVIDER` ('gemini' | 'ollama').
    """
    selected = (provider_name or settings.LLM_PROVIDER or "gemini").strip().lower()
    if selected == "gemini":
        return GeminiProvider(**kwargs)
    if selected == "ollama":
        return OllamaProvider(**kwargs)
    raise ValueError(
        f"LLM provider không được hỗ trợ: '{selected}'. Chỉ chấp nhận 'gemini' hoặc 'ollama'."
    )


def get_llm_provider() -> BaseLLMProvider:
    """Trả về LLM Provider đang được cấu hình trong `settings.LLM_PROVIDER`."""
    return create_llm_provider()
