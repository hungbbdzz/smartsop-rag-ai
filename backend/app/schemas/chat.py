from typing import Literal, Optional
from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    """Payload yêu cầu hỏi đáp Trợ lý Kỹ thuật RAG AI."""

    question: str = Field(..., min_length=1, max_length=1000, description="Câu hỏi kỹ thuật hoặc mã lỗi thiết bị")
    doc_id: Optional[str] = Field(None, description="Giới hạn tìm kiếm trong 1 tài liệu SOP cụ thể (tùy chọn)")
    top_k: int = Field(default=5, ge=1, le=15, description="Số đoạn ngữ cảnh tối đa truy hồi")
    temperature: float = Field(default=0.1, ge=0.0, le=1.0, description="Nhiệt độ sinh câu trả lời LLM")


class SseTokenEvent(BaseModel):
    type: Literal["token"] = "token"
    content: str


class SseCitationEvent(BaseModel):
    type: Literal["citation"] = "citation"
    doc_id: str
    doc_code: str = ""
    file: str
    page: int
    section_title: str = ""
    score: float
    snippet: str = ""


class SseDoneEvent(BaseModel):
    type: Literal["done"] = "done"
    audit_log_id: Optional[str] = None
    is_refused: bool = False
    ttft_ms: Optional[int] = None
    latency_ms: Optional[int] = None
    total_chars: int = 0
    top_score: float = 0.0
