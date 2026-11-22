from typing import Any, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.user import User


class ChatAuditLog(Base, TimestampMixin):
    """
    Bảng nhật ký kiểm toán hỏi đáp của Trợ lý RAG AI.
    Phục vụ giám sát tuân thủ, phát hiện câu hỏi ngoài luồng và tính toán SLA/Latency.
    """
    __tablename__ = "chat_audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    question: Mapped[str] = mapped_column(String(1000), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    cited_doc_ids: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)  # List[str]
    cited_pages: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)    # List[int]
    top_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_refused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ttft_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)      # Time To First Token (ms)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Tổng thời gian xử lý (ms)
    is_partial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    feedback_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1 - 5 sao

    # Quan hệ
    user: Mapped[Optional["User"]] = relationship("User", back_populates="chat_audit_logs")

    def __repr__(self) -> str:
        return f"<ChatAuditLog id={self.id} is_refused={self.is_refused}>"

