import enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.machine import Machine
    from app.models.user import User
    from app.models.sop_document import SOPDocument


class TicketPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"                # Mới tiếp nhận sự cố
    IN_PROGRESS = "IN_PROGRESS"  # Kỹ sư đang thao tác xử lý máy
    RESOLVED = "RESOLVED"        # Đã xử lý xong (phục hồi sản xuất)
    CLOSED = "CLOSED"            # Đã đóng và nghiệm thu


class IncidentTicket(Base, TimestampMixin):
    __tablename__ = "incident_tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    ticket_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    machine_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("machines.id", ondelete="CASCADE"), nullable=False
    )
    reported_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    error_code: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    priority: Mapped[TicketPriority] = mapped_column(
        SAEnum(TicketPriority, native_enum=False),
        default=TicketPriority.MEDIUM,
        nullable=False,
    )
    status: Mapped[TicketStatus] = mapped_column(
        SAEnum(TicketStatus, native_enum=False),
        default=TicketStatus.OPEN,
        nullable=False,
    )

    # Đề xuất tự động từ RAG AI
    suggested_sop_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("sop_documents.id", ondelete="SET NULL"), nullable=True
    )
    suggested_page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    suggested_snippet: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Dữ liệu tính toán MTTR
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Quan hệ
    machine: Mapped["Machine"] = relationship("Machine", back_populates="incident_tickets")
    reported_by_user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="incident_tickets"
    )
    suggested_sop: Mapped[Optional["SOPDocument"]] = relationship(
        "SOPDocument", back_populates="suggested_tickets"
    )

    def __repr__(self) -> str:
        return f"<IncidentTicket code={self.ticket_code} status={self.status} error={self.error_code}>"

