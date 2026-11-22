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


async def get_first_machine_id(client: AsyncClient, token: str) -> str:
    """Helper lấy ID của máy móc đầu tiên trong CSDL."""
    resp = await client.get("/api/v1/machines", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    machines = resp.json()
    assert len(machines) > 0
    return machines[0]["id"]


@pytest.mark.asyncio
async def test_operator_cannot_create_incident_ticket():
    """RBAC: Operator (công nhân) bị cấm tạo phiếu sự cố (nhận HTTP 403 Forbidden)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await get_token(client, "operator", "Operator@2026")
        machine_id = await get_first_machine_id(client, op_token)

        resp = await client.post(
            "/api/v1/incident_tickets",
            json={
                "machine_id": machine_id,
                "error_code": "E-204",
                "description": "Kẹt cuộn linh kiện feeder số 4",
                "priority": "HIGH",
            },
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert resp.status_code == 403


@pytest.mark.asyncio
async def test_gate_test_1_3_shift_engineer_create_ticket_success():
    """GATE TEST 1.3: Kỹ sư ca (SHIFT_ENGINEER) tạo phiếu sự cố thành công (HTTP 201)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        eng_token = await get_token(client, "engineer", "Engineer@2026")
        admin_token = await get_token(client, "admin", "Admin@2026")
        machine_id = await get_first_machine_id(client, eng_token)

        ticket_code = "INC-TEST-GATE-001"
        payload = {
            "ticket_code": ticket_code,
            "machine_id": machine_id,
            "error_code": "E-204",
            "description": "Lỗi lệch tọa độ hút gắp bản mạch chip IC",
            "priority": "CRITICAL",
        }

        created_id = None
        try:
            resp = await client.post(
                "/api/v1/incident_tickets",
                json=payload,
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert resp.status_code == 201
            data = resp.json()
            assert data["ticket_code"] == ticket_code
            assert data["error_code"] == "E-204"
            assert data["status"] == "OPEN"
            assert data["priority"] == "CRITICAL"
            created_id = data["id"]
        finally:
            if created_id:
                await client.delete(
                    f"/api/v1/incident_tickets/{created_id}",
                    headers={"Authorization": f"Bearer {admin_token}"},
                )


@pytest.mark.asyncio
async def test_gate_test_1_3_invalid_state_transition_open_to_resolved_blocked():
    """GATE TEST 1.3: Chuyển trạng thái từ OPEN thẳng sang RESOLVED bị chặn với HTTP 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        eng_token = await get_token(client, "engineer", "Engineer@2026")
        admin_token = await get_token(client, "admin", "Admin@2026")
        machine_id = await get_first_machine_id(client, eng_token)

        # 1. Tạo phiếu mới (trạng thái ban đầu: OPEN)
        create_resp = await client.post(
            "/api/v1/incident_tickets",
            json={
                "machine_id": machine_id,
                "error_code": "E-102",
                "description": "Cảm biến áp suất khí nén dưới ngưỡng",
                "priority": "MEDIUM",
            },
            headers={"Authorization": f"Bearer {eng_token}"},
        )
        assert create_resp.status_code == 201
        ticket = create_resp.json()
        ticket_id = ticket["id"]
        assert ticket["status"] == "OPEN"

        try:
            # 2. Cố tình chuyển thẳng sang RESOLVED -> Bị chặn với HTTP 400
            patch_resp = await client.patch(
                f"/api/v1/incident_tickets/{ticket_id}",
                json={"status": "RESOLVED"},
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert patch_resp.status_code == 400
            assert "Không thể chuyển trạng thái trực tiếp từ OPEN sang RESOLVED" in patch_resp.json()["detail"]

            # 3. Chuyển hợp lệ sang IN_PROGRESS -> Thành công
            progress_resp = await client.patch(
                f"/api/v1/incident_tickets/{ticket_id}",
                json={"status": "IN_PROGRESS"},
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert progress_resp.status_code == 200
            progress_data = progress_resp.json()
            assert progress_data["status"] == "IN_PROGRESS"
            assert progress_data["started_at"] is not None

            # 4. Từ IN_PROGRESS chuyển sang RESOLVED -> Thành công
            resolve_resp = await client.patch(
                f"/api/v1/incident_tickets/{ticket_id}",
                json={
                    "status": "RESOLVED",
                    "resolution_notes": "Đã vệ sinh van khí nén và hiệu chỉnh lại áp suất đạt chuẩn 0.5MPa",
                },
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert resolve_resp.status_code == 200
            resolve_data = resolve_resp.json()
            assert resolve_data["status"] == "RESOLVED"
            assert resolve_data["resolved_at"] is not None
            assert "0.5MPa" in resolve_data["resolution_notes"]
        finally:
            await client.delete(
                f"/api/v1/incident_tickets/{ticket_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )


@pytest.mark.asyncio
async def test_ticket_rbac_deletion_and_filtering():
    """Chỉ Admin mới có quyền xóa phiếu sự cố; kiểm tra tính năng lọc danh sách."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        eng_token = await get_token(client, "engineer", "Engineer@2026")
        admin_token = await get_token(client, "admin", "Admin@2026")
        op_token = await get_token(client, "operator", "Operator@2026")
        machine_id = await get_first_machine_id(client, eng_token)

        # 1. Tạo phiếu
        create_resp = await client.post(
            "/api/v1/incident_tickets",
            json={
                "machine_id": machine_id,
                "error_code": "ALM-99",
                "description": "Sự cố lọc thử nghiệm",
                "priority": "LOW",
            },
            headers={"Authorization": f"Bearer {eng_token}"},
        )
        assert create_resp.status_code == 201
        ticket_id = create_resp.json()["id"]

        try:
            # 2. Lọc theo error_code ALM-99
            list_resp = await client.get(
                "/api/v1/incident_tickets?error_code=ALM-99",
                headers={"Authorization": f"Bearer {op_token}"},
            )
            assert list_resp.status_code == 200
            results = list_resp.json()
            assert any(t["id"] == ticket_id for t in results)

            # 3. Kỹ sư cố xóa phiếu -> 403 Forbidden
            eng_del = await client.delete(
                f"/api/v1/incident_tickets/{ticket_id}",
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert eng_del.status_code == 403

            # 4. Admin xóa phiếu -> 200 OK
            adm_del = await client.delete(
                f"/api/v1/incident_tickets/{ticket_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert adm_del.status_code == 200

            # 5. Xác nhận không còn tồn tại -> 404
            get_resp = await client.get(
                f"/api/v1/incident_tickets/{ticket_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert get_resp.status_code == 404
        except Exception:
            # Fallback cleanup nếu có lỗi
            await client.delete(
                f"/api/v1/incident_tickets/{ticket_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            raise

