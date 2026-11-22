import enum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.production_line import ProductionLine
    from app.models.machine import Machine
    from app.models.user import User
    from app.models.sop_chunk import SOPChunk
    from app.models.incident_ticket import IncidentTicket


class IngestionStatus(str, enum.Enum):
    PENDING = "PENDING"          # Đang chờ xử lý
    PROCESSING = "PROCESSING"    # Đang bóc tách & tạo vector
    COMPLETED = "COMPLETED"      # Đã nạp vào ChromaDB thành công
    FAILED = "FAILED"            # Lỗi trong quá trình xử lý


class SOPDocument(Base, TimestampMixin):
    __tablename__ = "sop_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # SHA-256
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Bytes
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ingestion_status: Mapped[IngestionStatus] = mapped_column(
        SAEnum(IngestionStatus, native_enum=False),
        default=IngestionStatus.PENDING,
        nullable=False,
    )
    ingestion_error: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Khóa ngoại
    line_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("production_lines.id", ondelete="SET NULL"), nullable=True
    )
    machine_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("machines.id", ondelete="SET NULL"), nullable=True
    )
    uploaded_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Quan hệ
    production_line: Mapped[Optional["ProductionLine"]] = relationship(
        "ProductionLine", back_populates="sop_documents"
    )
    machine: Mapped[Optional["Machine"]] = relationship("Machine", back_populates="sop_documents")
    uploader: Mapped[Optional["User"]] = relationship("User", back_populates="uploaded_sops")
    chunks: Mapped[List["SOPChunk"]] = relationship(
        "SOPChunk", back_populates="document", cascade="all, delete-orphan"
    )
    suggested_tickets: Mapped[List["IncidentTicket"]] = relationship(
        "IncidentTicket", back_populates="suggested_sop"
    )

    def __repr__(self) -> str:
        return f"<SOPDocument code={self.document_code} status={self.ingestion_status}>"

