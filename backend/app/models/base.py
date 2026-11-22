import uuid
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String


class TimestampMixin:
    """Mixin tự động thêm thời gian tạo và cập nhật."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

# sinh khóa 36 kí tự
def generate_uuid() -> str:
    """Sinh UUIDv4 dạng chuỗi chuẩn tương thích cả PostgreSQL và SQLite."""
    return str(uuid.uuid4())

