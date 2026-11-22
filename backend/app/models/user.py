import enum
from typing import List, TYPE_CHECKING
from sqlalchemy import Boolean, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.incident_ticket import IncidentTicket
    from app.models.sop_document import SOPDocument
    from app.models.chat_audit_log import ChatAuditLog


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    FACTORY_MANAGER = "FACTORY_MANAGER"
    SHIFT_ENGINEER = "SHIFT_ENGINEER"
    OPERATOR = "OPERATOR"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, native_enum=False),
        default=UserRole.OPERATOR,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Quan hệ
    incident_tickets: Mapped[List["IncidentTicket"]] = relationship(
        "IncidentTicket", back_populates="reported_by_user"
    )
    uploaded_sops: Mapped[List["SOPDocument"]] = relationship(
        "SOPDocument", back_populates="uploader"
    )
    chat_audit_logs: Mapped[List["ChatAuditLog"]] = relationship(
        "ChatAuditLog", back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User username={self.username} role={self.role}>"

