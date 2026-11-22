import pytest
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import verify_password
from app.models.user import User, UserRole
from app.models.production_line import ProductionLine
from app.models.machine import Machine
from app.models.sop_document import SOPDocument


@pytest.mark.asyncio
async def test_database_seeded_users():
    """Kiểm tra Gate Test 1.1: 4 tài khoản người dùng thuộc 4 roles đã được nạp."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        assert len(users) >= 4

        usernames = {u.username for u in users}
        assert "admin" in usernames
        assert "manager" in usernames
        assert "engineer" in usernames
        assert "operator" in usernames

        # Kiểm tra mật khẩu admin
        admin_user = next(u for u in users if u.username == "admin")
        assert admin_user.role == UserRole.ADMIN
        assert verify_password("Admin@2026", admin_user.password_hash) is True
        assert verify_password("WrongPassword", admin_user.password_hash) is False


@pytest.mark.asyncio
async def test_database_seeded_lines_and_machines():
    """Kiểm tra Gate Test 1.1: 2 dây chuyền SMT và 5 máy móc thiết bị."""
    async with AsyncSessionLocal() as session:
        # Kiểm tra dây chuyền
        lines_res = await session.execute(select(ProductionLine))
        lines = lines_res.scalars().all()
        assert len(lines) >= 2

        # Kiểm tra máy móc
        machines_res = await session.execute(select(Machine))
        machines = machines_res.scalars().all()
        assert len(machines) >= 5

        machine_codes = {m.machine_code for m in machines}
        assert "SMT-FUJI-01" in machine_codes
        assert "REFLOW-HELLER-01" in machine_codes
        assert "AOI-KOHYOUNG-01" in machine_codes


@pytest.mark.asyncio
async def test_database_seeded_sop_documents():
    """Kiểm tra Gate Test 1.1: 3 tài liệu SOP mẫu có metadata hợp lệ."""
    async with AsyncSessionLocal() as session:
        sops_res = await session.execute(select(SOPDocument))
        sops = sops_res.scalars().all()
        assert len(sops) >= 3

        doc_codes = {s.document_code for s in sops}
        assert "SOP-SMT-001-VN" in doc_codes
        assert "SOP-REFLOW-002-VN" in doc_codes
        assert "SOP-AOI-003-VN" in doc_codes

        for s in sops:
            assert len(s.file_hash) == 64
            assert s.file_hash != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            assert s.page_count > 0
            assert s.file_size is not None and s.file_size > 0

