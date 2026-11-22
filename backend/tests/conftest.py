import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from scripts.seed_data import seed_data


def pytest_sessionstart(session):
    """
    Hook chuẩn của Pytest chạy trước toàn bộ test suite:
    Tự động khởi tạo 7 bảng và nạp seed data nếu CSDL trống.
    Đảm bảo 100% Reproducibility trên mọi máy clone mới.
    """
    async def init_test_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as db_session:
            result = await db_session.execute(select(User))
            users = result.scalars().all()
            if len(users) < 4:
                await seed_data()

    try:
        asyncio.run(init_test_db())
    except Exception as e:
        print(f"[conftest] Cảnh báo khởi tạo test database: {e}")

