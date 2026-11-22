from datetime import timedelta
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app


@pytest.mark.asyncio
async def test_login_success_admin():
    """Gate Test 1.2: Đăng nhập thành công với tài khoản Admin."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@2026"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 480 * 60  # 8 tiếng
        assert data["user"]["username"] == "admin"
        assert data["user"]["role"] == "ADMIN"
        assert data["user"]["is_active"] is True
        # Đảm bảo password_hash không bao giờ bị trả về
        assert "password_hash" not in data["user"]


@pytest.mark.asyncio
async def test_login_success_other_roles():
    """Gate Test 1.2: Đăng nhập thành công với các vai trò Manager, Engineer, Operator."""
    accounts = [
        ("manager", "Manager@2026", "FACTORY_MANAGER"),
        ("engineer", "Engineer@2026", "SHIFT_ENGINEER"),
        ("operator", "Operator@2026", "OPERATOR"),
    ]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for username, password, expected_role in accounts:
            response = await client.post(
                "/api/v1/auth/login",
                json={"username": username, "password": password},
            )
            assert response.status_code == 200, f"Đăng nhập thất bại cho user {username}"
            data = response.json()
            assert data["user"]["role"] == expected_role


@pytest.mark.asyncio
async def test_login_wrong_password():
    """Gate Test 1.2: Đăng nhập sai mật khẩu phải trả về HTTP 401 Unauthorized."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "WrongPassword@999"},
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "không chính xác" in data["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user():
    """Gate Test 1.2: Đăng nhập với tài khoản không tồn tại phải trả về HTTP 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "ghost_user", "password": "Password@123"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_profile_success():
    """Gate Test 1.2: Lấy thông tin cá nhân với Bearer Token hợp lệ (GET /auth/me)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Đăng nhập lấy token
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@2026"},
        )
        token = login_resp.json()["access_token"]

        # 2. Gọi GET /auth/me kèm token
        me_resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        user_data = me_resp.json()
        assert user_data["username"] == "admin"
        assert user_data["role"] == "ADMIN"
        assert "password_hash" not in user_data


@pytest.mark.asyncio
async def test_get_current_user_no_token():
    """Gate Test 1.2: Gọi API bảo vệ mà không gửi token -> HTTP 401 Unauthorized."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """Gate Test 1.2: Gửi token rác/giả mạo -> HTTP 401 Unauthorized."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer token_gia_mao_khong_hop_le_123"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_expired_token():
    """Gate Test 1.2: Gửi token đã hết hạn -> HTTP 401 Unauthorized."""
    # Tạo 1 token đã hết hạn 10 phút trước
    expired_token = create_access_token(
        data={"sub": "any_user_id", "username": "admin", "role": "ADMIN"},
        expires_delta=timedelta(minutes=-10),
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401
