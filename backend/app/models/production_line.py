from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.machine import Machine
    from app.models.sop_document import SOPDocument


class ProductionLine(Base, TimestampMixin):
    __tablename__ = "production_lines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    factory_zone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Quan hệ
    machines: Mapped[List["Machine"]] = relationship(
        "Machine", back_populates="line", cascade="all, delete-orphan"
    )
    sop_documents: Mapped[List["SOPDocument"]] = relationship(
        "SOPDocument", back_populates="production_line"
    )

    def __repr__(self) -> str:
        return f"<ProductionLine name={self.name}>"

