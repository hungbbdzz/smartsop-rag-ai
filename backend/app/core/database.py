import os
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Đảm bảo thư mục dữ liệu tồn tại nếu dùng SQLite
if "sqlite" in settings.DATABASE_URL:
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

# Khởi tạo Async Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    # Chỉ bật connect_args cho SQLite nếu cần
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

# Session factory bất đồng bộ
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(AsyncAttrs, DeclarativeBase):
    """Lớp cơ sở cho toàn bộ SQLAlchemy 2.0 models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency cung cấp AsyncSession cho mỗi HTTP request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

