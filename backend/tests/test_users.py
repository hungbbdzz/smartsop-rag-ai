import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


async def get_token(client: AsyncClient, username: str, password: str) -> str:
    """Helper đăng nhập lấy Bearer token."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200, f"Đăng nhập thất bại: {resp.text}"
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_users_rbac_forbidden_for_non_admins():
    """Nhân sự không phải Admin (Operator, Engineer, Manager) đều nhận 403 khi thao tác Quản trị người dùng."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await get_token(client, "operator", "Operator@2026")
        eng_token = await get_token(client, "engineer", "Engineer@2026")
        mgr_token = await get_token(client, "manager", "Manager@2026")

        for token in [op_token, eng_token, mgr_token]:
            # Thử xem danh sách
            resp_list = await client.get(
                "/api/v1/users",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp_list.status_code == 403

            # Thử tạo user
            resp_create = await client.post(
                "/api/v1/users",
                json={
                    "username": "hacker",
                    "email": "hacker@smartsop.com",
                    "full_name": "Hacker",
                    "role": "OPERATOR",
                    "password": "Password@123",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp_create.status_code == 403


@pytest.mark.asyncio
async def test_admin_list_users_and_filters():
    """Admin xem danh sách nhân sự và lọc theo Role/Trạng thái hoạt động."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        admin_token = await get_token(client, "admin", "Admin@2026")

        # 1. Lấy toàn bộ danh sách
        resp = await client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        users = resp.json()
        assert len(users) >= 4
        # Kiểm tra không lộ trường mật khẩu
        for u in users:
            assert "password_hash" not in u
            assert "password" not in u

        # 2. Lọc theo role OPERATOR
        resp_op = await client.get(
            "/api/v1/users?role=OPERATOR",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp_op.status_code == 200
        ops = resp_op.json()
        assert all(u["role"] == "OPERATOR" for u in ops)

        # 3. Lọc theo is_active=True
        resp_active = await client.get(
            "/api/v1/users?is_active=true",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp_active.status_code == 200
        actives = resp_active.json()
        assert all(u["is_active"] is True for u in actives)


@pytest.mark.asyncio
async def test_admin_create_user_and_duplicate_validation():
    """Admin tạo tài khoản nhân sự mới và kiểm tra ngăn chặn trùng lặp email/username."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        admin_token = await get_token(client, "admin", "Admin@2026")

        # Đảm bảo môi trường sạch trước khi chạy
        list_resp = await client.get("/api/v1/users", headers={"Authorization": f"Bearer {admin_token}"})
        for u in list_resp.json():
            if u["username"] == "technician_01":
                await client.delete(f"/api/v1/users/{u['id']}", headers={"Authorization": f"Bearer {admin_token}"})

        new_user_payload = {
            "username": "technician_01",
            "email": "technician01@smartsop.vn",
            "full_name": "Kỹ thuật viên SMT 01",
            "role": "OPERATOR",
            "password": "TechPassword@2026",
            "is_active": True,
        }

        created_id = None
        try:
            # 1. Tạo mới thành công
            resp_create = await client.post(
                "/api/v1/users",
                json=new_user_payload,
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp_create.status_code == 201
            created_user = resp_create.json()
            assert created_user["username"] == "technician_01"
            assert created_user["email"] == "technician01@smartsop.vn"
            assert "password_hash" not in created_user
            created_id = created_user["id"]

            # 2. Thử tạo lại với cùng username -> 400 Bad Request
            resp_dup_username = await client.post(
                "/api/v1/users",
                json={**new_user_payload, "email": "other_email@smartsop.vn"},
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp_dup_username.status_code == 400
            assert "Tên đăng nhập" in resp_dup_username.json()["detail"]

            # 3. Thử tạo lại với cùng email -> 400 Bad Request
            resp_dup_email = await client.post(
                "/api/v1/users",
                json={**new_user_payload, "username": "technician_diff"},
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp_dup_email.status_code == 400
            assert "email" in resp_dup_email.json()["detail"].lower()

            # 4. Xác thực đăng nhập bằng tài khoản vừa tạo
            tech_token = await get_token(client, "technician_01", "TechPassword@2026")
            assert tech_token is not None
        finally:
            if created_id:
                await client.delete(f"/api/v1/users/{created_id}", headers={"Authorization": f"Bearer {admin_token}"})


@pytest.mark.asyncio
async def test_admin_update_and_delete_user():
    """Admin cập nhật thông tin user, kiểm tra ngăn tự xóa bản thân và xóa user thành công."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        admin_token = await get_token(client, "admin", "Admin@2026")

        # 1. Lấy thông tin admin hiện tại
        me_resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        admin_id = me_resp.json()["id"]

        # 2. Thử xóa chính tài khoản Admin -> 400 Bad Request
        resp_self_del = await client.delete(
            f"/api/v1/users/{admin_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp_self_del.status_code == 400
        assert "không thể tự xóa" in resp_self_del.json()["detail"]

        # 3. Tạo một user tạm để test update & delete
        temp_user_resp = await client.post(
            "/api/v1/users",
            json={
                "username": "temp_user_for_delete",
                "email": "temp_delete@smartsop.vn",
                "full_name": "Nhân viên Tạm",
                "role": "OPERATOR",
                "password": "TempPassword@123",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert temp_user_resp.status_code == 201
        temp_id = temp_user_resp.json()["id"]

        # 4. Cập nhật role thành SHIFT_ENGINEER
        patch_resp = await client.patch(
            f"/api/v1/users/{temp_id}",
            json={"role": "SHIFT_ENGINEER", "full_name": "Kỹ sư Thử Nghiệm"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["role"] == "SHIFT_ENGINEER"
        assert patch_resp.json()["full_name"] == "Kỹ sư Thử Nghiệm"

        # 5. Xóa user tạm -> 200 OK
        del_resp = await client.delete(
            f"/api/v1/users/{temp_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert del_resp.status_code == 200

        # 6. Kiểm tra lại user đã biến mất -> 404 Not Found
        get_resp = await client.get(
            f"/api/v1/users/{temp_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert get_resp.status_code == 404
