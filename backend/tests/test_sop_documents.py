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
async def test_list_sop_documents_operator_allowed():
    """Công nhân (Operator) có quyền xem danh mục tài liệu SOP."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await get_token(client, "operator", "Operator@2026")
        resp = await client.get(
            "/api/v1/sop_documents",
            headers={"Authorization": f"Bearer {op_token}"},
        )
        assert resp.status_code == 200
        docs = resp.json()
        assert len(docs) >= 3
        codes = [d["document_code"] for d in docs]
        assert any("SOP-SMT-001" in c for c in codes)


@pytest.mark.asyncio
async def test_sop_upload_rbac_operator_and_engineer_blocked():
    """RBAC: Operator và Shift Engineer không có quyền upload tài liệu SOP (HTTP 403 Forbidden)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await get_token(client, "operator", "Operator@2026")
        eng_token = await get_token(client, "engineer", "Engineer@2026")

        pdf_bytes = make_pdf_bytes("Blocked SOP")
        for token in [op_token, eng_token]:
            files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
            data = {
                "document_code": "SOP-TEST-BLOCK",
                "title": "Tài liệu thử nghiệm phân quyền",
            }
            resp = await client.post(
                "/api/v1/sop_documents/upload",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 403


@pytest.mark.asyncio
async def test_gate_test_1_3_upload_pdf_and_duplicate_hash_blocked():
    """GATE TEST 1.3: Manager upload file PDF thành công, upload lần 2 phát hiện trùng SHA-256 (HTTP 400)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        mgr_token = await get_token(client, "manager", "Manager@2026")
        admin_token = await get_token(client, "admin", "Admin@2026")

        pdf_bytes = make_pdf_bytes("Unique Test SOP Gate 1.3")
        created_id = None
        try:
            # 1. Upload lần 1 -> 201 Created
            files = {"file": ("unique_sop.pdf", pdf_bytes, "application/pdf")}
            data = {
                "document_code": "SOP-TEST-GATE-001",
                "title": "Quy trình thử nghiệm Gate Test 1.3",
                "version": "1.0",
            }
            resp1 = await client.post(
                "/api/v1/sop_documents/upload",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {mgr_token}"},
            )
            assert resp1.status_code == 201
            doc_data = resp1.json()
            assert doc_data["document_code"] == "SOP-TEST-GATE-001"
            assert doc_data["page_count"] == 1
            created_id = doc_data["id"]

            # 2. Upload lần 2 (cùng file PDF, khác mã code) -> Phát hiện trùng SHA-256 -> 400 Bad Request
            files_dup = {"file": ("another_name.pdf", pdf_bytes, "application/pdf")}
            data_dup = {
                "document_code": "SOP-TEST-GATE-002",
                "title": "Cố tình nạp file trùng băm",
            }
            resp2 = await client.post(
                "/api/v1/sop_documents/upload",
                files=files_dup,
                data=data_dup,
                headers={"Authorization": f"Bearer {mgr_token}"},
            )
            assert resp2.status_code == 400
            assert "trùng lặp mã băm SHA-256" in resp2.json()["detail"]
        finally:
            if created_id:
                await client.delete(
                    f"/api/v1/sop_documents/{created_id}",
                    headers={"Authorization": f"Bearer {admin_token}"},
                )


@pytest.mark.asyncio
async def test_gate_test_1_3_secure_pdf_streaming_and_deletion_rbac():
    """GATE TEST 1.3: GET /sop_documents/{id}/file yêu cầu xác thực Bearer; chỉ Admin mới xóa được SOP."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        mgr_token = await get_token(client, "manager", "Manager@2026")
        admin_token = await get_token(client, "admin", "Admin@2026")
        op_token = await get_token(client, "operator", "Operator@2026")

        # 1. Manager tạo SOP mới để thử nghiệm luồng file
        pdf_bytes = make_pdf_bytes("Secure File Streaming Test")
        files = {"file": ("secure_stream.pdf", pdf_bytes, "application/pdf")}
        data = {
            "document_code": "SOP-STREAM-001",
            "title": "Tài liệu kiểm thử luồng nhị phân an toàn",
        }
        create_resp = await client.post(
            "/api/v1/sop_documents/upload",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {mgr_token}"},
        )
        assert create_resp.status_code == 201
        doc_id = create_resp.json()["id"]

        try:
            # 2. Truy cập không có Bearer token -> 401 Unauthorized
            unauth_resp = await client.get(f"/api/v1/sop_documents/{doc_id}/file")
            assert unauth_resp.status_code in [401, 403]

            # 3. Operator có Bearer token hợp lệ -> Nhận luồng nhị phân 200 OK với content-type application/pdf
            auth_resp = await client.get(
                f"/api/v1/sop_documents/{doc_id}/file",
                headers={"Authorization": f"Bearer {op_token}"},
            )
            assert auth_resp.status_code == 200
            assert "application/pdf" in auth_resp.headers["content-type"]
            assert len(auth_resp.content) == len(pdf_bytes)

            # 4. Manager cố tình xóa SOP -> 403 Forbidden (chỉ Admin mới có quyền xóa tài liệu)
            mgr_del = await client.delete(
                f"/api/v1/sop_documents/{doc_id}",
                headers={"Authorization": f"Bearer {mgr_token}"},
            )
            assert mgr_del.status_code == 403

            # 5. Admin xóa SOP -> 200 OK
            admin_del = await client.delete(
                f"/api/v1/sop_documents/{doc_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert admin_del.status_code == 200

            # 6. Kiểm tra lại sau khi xóa -> 404 Not Found
            check_resp = await client.get(
                f"/api/v1/sop_documents/{doc_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert check_resp.status_code == 404
        except Exception:
            await client.delete(
                f"/api/v1/sop_documents/{doc_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            raise
