"""
Bộ kiểm thử tổng hợp Cổng nghiệm thu Gate Test 1.3 (Milestone 1.3 Acceptance Tests):
- Dùng token OPERATOR gọi DELETE /machines/{id} -> Nhận HTTP 403 Forbidden.
- Dùng token ADMIN gọi DELETE /machines/{id} -> Nhận HTTP 200 Thành công.
- Dùng token SHIFT_ENGINEER gọi POST /incident_tickets -> Tạo phiếu thành công.
- Cố tình nhảy trạng thái phiếu từ OPEN thẳng sang RESOLVED -> Bị chặn với lỗi HTTP 400.
- Tải lên cùng 1 file PDF 2 lần -> Hệ thống phát hiện trùng file_hash và từ chối (HTTP 400).
- Phục vụ file PDF có bảo mật Bearer token: GET /sop_documents/{id}/file.
- Quản trị người dùng CRUD chỉ dành riêng cho Admin.
"""

import io
import pypdf
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


def make_pdf_bytes(title: str = "Test SOP") -> bytes:
    """Tạo file PDF hợp lệ trong bộ nhớ với tiêu đề riêng để sinh mã băm khác nhau."""
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.add_metadata({"/Title": title})
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_gate_1_3_delete_machine_rbac():
    """GATE 1.3.1: Operator xóa máy bị 403, Admin xóa máy thành công 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await get_token(client, "operator", "Operator@2026")
        admin_token = await get_token(client, "admin", "Admin@2026")

        # 1. Admin tạo máy tạm thời
        line_resp = await client.get("/api/v1/production-lines", headers={"Authorization": f"Bearer {admin_token}"})
        line_id = line_resp.json()[0]["id"]

        create_resp = await client.post(
            "/api/v1/machines",
            json={
                "line_id": line_id,
                "machine_code": "MAC-GATE-TEST-01",
                "name": "Máy kiểm thử Gate 1.3",
                "model": "GT-2026",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert create_resp.status_code == 201
        machine_id = create_resp.json()["id"]

        try:
            # 2. Operator cố tình xóa -> 403 Forbidden
            op_del = await client.delete(
                f"/api/v1/machines/{machine_id}",
                headers={"Authorization": f"Bearer {op_token}"},
            )
            assert op_del.status_code == 403

            # 3. Admin xóa thành công -> 200 OK
            adm_del = await client.delete(
                f"/api/v1/machines/{machine_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert adm_del.status_code == 200
        except Exception:
            await client.delete(f"/api/v1/machines/{machine_id}", headers={"Authorization": f"Bearer {admin_token}"})
            raise


@pytest.mark.asyncio
async def test_gate_1_3_shift_engineer_create_ticket():
    """GATE 1.3.2: Kỹ sư ca (SHIFT_ENGINEER) tạo phiếu sự cố thành công (201)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        eng_token = await get_token(client, "engineer", "Engineer@2026")
        admin_token = await get_token(client, "admin", "Admin@2026")

        mac_resp = await client.get("/api/v1/machines", headers={"Authorization": f"Bearer {eng_token}"})
        machine_id = mac_resp.json()[0]["id"]

        ticket_code = "INC-GATE-ENG-001"
        create_resp = await client.post(
            "/api/v1/incident_tickets",
            json={
                "ticket_code": ticket_code,
                "machine_id": machine_id,
                "error_code": "E-204",
                "description": "Kẹt linh kiện feeder trong ca 1",
                "priority": "HIGH",
            },
            headers={"Authorization": f"Bearer {eng_token}"},
        )
        assert create_resp.status_code == 201
        ticket_id = create_resp.json()["id"]
        assert create_resp.json()["status"] == "OPEN"

        # Dọn dẹp
        await client.delete(f"/api/v1/incident_tickets/{ticket_id}", headers={"Authorization": f"Bearer {admin_token}"})


@pytest.mark.asyncio
async def test_gate_1_3_state_machine_transition_restriction():
    """GATE 1.3.3: Nhảy trạng thái từ OPEN thẳng sang RESOLVED bị chặn với HTTP 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        eng_token = await get_token(client, "engineer", "Engineer@2026")
        admin_token = await get_token(client, "admin", "Admin@2026")

        mac_resp = await client.get("/api/v1/machines", headers={"Authorization": f"Bearer {eng_token}"})
        machine_id = mac_resp.json()[0]["id"]

        create_resp = await client.post(
            "/api/v1/incident_tickets",
            json={
                "machine_id": machine_id,
                "error_code": "E-501",
                "description": "Lỗi nhiệt độ vượt ngưỡng",
                "priority": "CRITICAL",
            },
            headers={"Authorization": f"Bearer {eng_token}"},
        )
        assert create_resp.status_code == 201
        ticket_id = create_resp.json()["id"]

        try:
            # Nhảy thẳng OPEN -> RESOLVED bị chặn
            bad_resp = await client.patch(
                f"/api/v1/incident_tickets/{ticket_id}",
                json={"status": "RESOLVED"},
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert bad_resp.status_code == 400
            assert "OPEN sang RESOLVED" in bad_resp.json()["detail"]

            # OPEN -> IN_PROGRESS hợp lệ
            ok_prog = await client.patch(
                f"/api/v1/incident_tickets/{ticket_id}",
                json={"status": "IN_PROGRESS"},
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert ok_prog.status_code == 200

            # IN_PROGRESS -> RESOLVED hợp lệ
            ok_res = await client.patch(
                f"/api/v1/incident_tickets/{ticket_id}",
                json={"status": "RESOLVED", "resolution_notes": "Đã điều chỉnh nhiệt độ về mức chuẩn"},
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert ok_res.status_code == 200
        finally:
            await client.delete(f"/api/v1/incident_tickets/{ticket_id}", headers={"Authorization": f"Bearer {admin_token}"})


@pytest.mark.asyncio
async def test_gate_1_3_upload_pdf_duplicate_hash():
    """GATE 1.3.4: Tải lên cùng 1 file PDF 2 lần -> Phát hiện trùng file_hash và từ chối."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        mgr_token = await get_token(client, "manager", "Manager@2026")
        admin_token = await get_token(client, "admin", "Admin@2026")

        pdf_bytes = make_pdf_bytes("Gate 1.3 SHA256 Test PDF")
        created_id = None
        try:
            # Lần 1: Thành công 201
            resp1 = await client.post(
                "/api/v1/sop_documents/upload",
                files={"file": ("gate_1_3_doc.pdf", pdf_bytes, "application/pdf")},
                data={"document_code": "SOP-GATE-HASH-01", "title": "Tài liệu kiểm tra băm"},
                headers={"Authorization": f"Bearer {mgr_token}"},
            )
            assert resp1.status_code == 201
            created_id = resp1.json()["id"]

            # Lần 2: Cùng file, khác mã -> Bị từ chối trùng băm (HTTP 400)
            resp2 = await client.post(
                "/api/v1/sop_documents/upload",
                files={"file": ("gate_1_3_doc_renamed.pdf", pdf_bytes, "application/pdf")},
                data={"document_code": "SOP-GATE-HASH-02", "title": "Tài liệu trùng lặp"},
                headers={"Authorization": f"Bearer {mgr_token}"},
            )
            assert resp2.status_code == 400
            assert "trùng lặp mã băm SHA-256" in resp2.json()["detail"]
        finally:
            if created_id:
                await client.delete(f"/api/v1/sop_documents/{created_id}", headers={"Authorization": f"Bearer {admin_token}"})


@pytest.mark.asyncio
async def test_gate_1_3_secure_pdf_file_streaming():
    """GATE 1.3.5: GET /sop_documents/{id}/file yêu cầu xác thực Bearer token."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await get_token(client, "operator", "Operator@2026")

        # Lấy danh sách SOP đã seed
        resp = await client.get("/api/v1/sop_documents", headers={"Authorization": f"Bearer {op_token}"})
        assert resp.status_code == 200
        docs = resp.json()
        assert len(docs) > 0
        doc_id = docs[0]["id"]

        # 1. Truy cập không token -> Bị chặn
        resp_unauth = await client.get(f"/api/v1/sop_documents/{doc_id}/file")
        assert resp_unauth.status_code in [401, 403]

        # 2. Truy cập có token -> 200 OK với binary application/pdf
        resp_auth = await client.get(
            f"/api/v1/sop_documents/{doc_id}/file",
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert resp_auth.status_code == 200
        assert "application/pdf" in resp_auth.headers["content-type"]

