import enum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Enum as SAEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.production_line import ProductionLine
    from app.models.sop_document import SOPDocument
    from app.models.incident_ticket import IncidentTicket


class MachineStatus(str, enum.Enum):
    OPERATIONAL = "OPERATIONAL"    # Đang vận hành bình thường
    MAINTENANCE = "MAINTENANCE"    # Đang bảo trì định kỳ
    ERROR = "ERROR"                # Đang dừng do sự cố kỹ thuật


class Machine(Base, TimestampMixin):
    __tablename__ = "machines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    machine_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[MachineStatus] = mapped_column(
        SAEnum(MachineStatus, native_enum=False),
        default=MachineStatus.OPERATIONAL,
        nullable=False,
    )
    line_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("production_lines.id", ondelete="CASCADE"), nullable=False
    )

    # Quan hệ
    line: Mapped["ProductionLine"] = relationship("ProductionLine", back_populates="machines")
    sop_documents: Mapped[List["SOPDocument"]] = relationship(
        "SOPDocument", back_populates="machine"
    )
    incident_tickets: Mapped[List["IncidentTicket"]] = relationship(
        "IncidentTicket", back_populates="machine", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Machine code={self.machine_code} status={self.status}>"

