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
async def test_list_production_lines_operator_allowed():
    """Bất kỳ nhân sự nào (kể cả Operator) đều có thể xem danh sách dây chuyền."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await get_token(client, "operator", "Operator@2026")
        resp = await client.get(
            "/api/v1/production-lines",
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert resp.status_code == 200
        lines = resp.json()
        assert len(lines) >= 2
        line_names = [l["name"] for l in lines]
        assert any("Dây chuyền SMT" in name for name in line_names)


@pytest.mark.asyncio
async def test_create_and_delete_production_line_rbac():
    """RBAC: Operator bị chặn tạo dây chuyền (403), Manager tạo được (201), chỉ Admin mới xóa được."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await get_token(client, "operator", "Operator@2026")
        mgr_token = await get_token(client, "manager", "Manager@2026")
        admin_token = await get_token(client, "admin", "Admin@2026")

        line_payload = {
            "name": "Dây chuyền Thử Nghiệm Line 99",
            "factory_zone": "Khu C - Thử nghiệm",
            "description": "Dây chuyền phục vụ kiểm thử tự động",
        }

        # 1. Operator cố tình tạo dây chuyền -> 403 Forbidden
        resp_op = await client.post(
            "/api/v1/production-lines",
            json=line_payload,
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert resp_op.status_code == 403

        # 2. Manager tạo dây chuyền thành công -> 201 Created
        resp_mgr = await client.post(
            "/api/v1/production-lines",
            json=line_payload,
            headers={"Authorization": f"Bearer {mgr_token}"},
        )
        assert resp_mgr.status_code == 201
        created_line = resp_mgr.json()
        line_id = created_line["id"]

        # 3. Tạo lại trùng tên -> 400 Bad Request
        resp_dup = await client.post(
            "/api/v1/production-lines",
            json=line_payload,
            headers={"Authorization": f"Bearer {mgr_token}"},
        )
        assert resp_dup.status_code == 400

        # 4. Manager cố tình xóa dây chuyền -> 403 Forbidden (chỉ Admin mới được xóa)
        resp_mgr_del = await client.delete(
            f"/api/v1/production-lines/{line_id}",
            headers={"Authorization": f"Bearer {mgr_token}"},
        )
        assert resp_mgr_del.status_code == 403

        # 5. Admin xóa dây chuyền thành công -> 200 OK
        resp_adm_del = await client.delete(
            f"/api/v1/production-lines/{line_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp_adm_del.status_code == 200


@pytest.mark.asyncio
async def test_list_machines_and_filtering():
    """Kiểm tra lấy danh sách máy và tính năng lọc theo status / line_id."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await get_token(client, "operator", "Operator@2026")

        # 1. Lấy tất cả máy
        resp = await client.get(
            "/api/v1/machines",
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert resp.status_code == 200
        machines = resp.json()
        assert len(machines) >= 5

        # 2. Lọc theo trạng thái OPERATIONAL
        resp_filtered = await client.get(
            "/api/v1/machines?status=OPERATIONAL",
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert resp_filtered.status_code == 200
        for m in resp_filtered.json():
            assert m["status"] == "OPERATIONAL"


@pytest.mark.asyncio
async def test_create_machine_validation_and_rbac():
    """Kiểm tra ràng buộc mã máy, tồn tại dây chuyền và phân quyền tạo máy."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await get_token(client, "operator", "Operator@2026")
        admin_token = await get_token(client, "admin", "Admin@2026")

        # Lấy một line_id hợp lệ
        lines_resp = await client.get(
            "/api/v1/production-lines",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        valid_line_id = lines_resp.json()[0]["id"]

        machine_payload = {
            "machine_code": "TEST-SMT-999",
            "name": "Máy kiểm thử tự động SMT Test",
            "model": "Model-99",
            "manufacturer": "Test Tech",
            "status": "OPERATIONAL",
            "line_id": valid_line_id,
        }

        # 1. Operator cố tình tạo máy -> 403
        resp_op = await client.post(
            "/api/v1/machines",
            json=machine_payload,
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert resp_op.status_code == 403

        # 2. Admin tạo với line_id giả mạo không tồn tại -> 404
        bad_payload = dict(machine_payload)
        bad_payload["line_id"] = "fake-line-id-not-found"
        resp_bad_line = await client.post(
            "/api/v1/machines",
            json=bad_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp_bad_line.status_code == 404

        # 3. Admin tạo thành công -> 201
        resp_adm = await client.post(
            "/api/v1/machines",
            json=machine_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp_adm.status_code == 201
        created_machine = resp_adm.json()
        assert created_machine["machine_code"] == "TEST-SMT-999"

        # 4. Trùng mã máy -> 400
        resp_dup = await client.post(
            "/api/v1/machines",
            json=machine_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp_dup.status_code == 400

        # Dọn dẹp máy test
        del_resp = await client.delete(
            f"/api/v1/machines/{created_machine['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert del_resp.status_code == 200


@pytest.mark.asyncio
async def test_gate_test_1_3_delete_machine_rbac():
    """
    GATE TEST 1.3 CỐT LÕI:
    - Dùng token OPERATOR gọi DELETE /machines/{id} -> Nhận HTTP 403 Forbidden.
    - Dùng token ADMIN gọi DELETE /machines/{id} -> Nhận HTTP 200 Thành công.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await get_token(client, "operator", "Operator@2026")
        admin_token = await get_token(client, "admin", "Admin@2026")

        # 1. Admin tạo một máy tạm để test xóa
        lines_resp = await client.get(
            "/api/v1/production-lines",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        line_id = lines_resp.json()[0]["id"]

        create_resp = await client.post(
            "/api/v1/machines",
            json={
                "machine_code": "SMT-TEMP-GATE-TEST",
                "name": "Máy tạm kiểm tra Gate Test 1.3",
                "status": "OPERATIONAL",
                "line_id": line_id,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert create_resp.status_code == 201
        temp_machine_id = create_resp.json()["id"]

        # 2. [GATE TEST 1.3] Operator cố tình xóa máy -> Phải nhận HTTP 403 Forbidden
        del_by_op = await client.delete(
            f"/api/v1/machines/{temp_machine_id}",
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert del_by_op.status_code == 403, "Operator không được phép xóa máy!"

        # 3. [GATE TEST 1.3] Admin xóa máy -> Phải nhận HTTP 200 Thành công
        del_by_admin = await client.delete(
            f"/api/v1/machines/{temp_machine_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert del_by_admin.status_code == 200, "Admin phải xóa máy thành công!"

        # 4. Kiểm tra máy đã thực sự bị xóa (404)
        get_resp = await client.get(
            f"/api/v1/machines/{temp_machine_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert get_resp.status_code == 404

