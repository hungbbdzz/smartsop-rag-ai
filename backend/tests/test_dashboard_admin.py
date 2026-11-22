"""
Unit & Integration test suite cho Dashboard KPI Analytics (/api/v1/dashboard)
và System Administration (/api/v1/admin):
- Phân quyền RBAC cho Dashboard (Operator bị 403, Engineer+ được 200)
- Tính toán chính xác MTTR (phút), đếm ticket và Top mã lỗi
- Phân quyền RBAC Admin-only cho /admin/audit_logs và /admin/system_status
- Lọc audit logs theo is_refused và kiểm tra payload system_status
"""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import delete, select

import app.routers.admin as admin_router_module
from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.chat_audit_log import ChatAuditLog
from app.models.incident_ticket import IncidentTicket, TicketPriority, TicketStatus
from app.models.machine import Machine


async def _get_token(client: AsyncClient, username: str, password: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_dashboard_rbac_operator_forbidden_engineer_allowed():
    """Operator bị chặn xem Dashboard (403); Kỹ sư ca trở lên xem được KPI & Charts (200)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await _get_token(client, "operator", "Operator@2026")
        eng_token = await _get_token(client, "engineer", "Engineer@2026")

        for path in ("/api/v1/dashboard/kpi", "/api/v1/dashboard/charts"):
            resp_op = await client.get(path, headers={"Authorization": f"Bearer {op_token}"})
            assert resp_op.status_code == 403

            resp_eng = await client.get(path, headers={"Authorization": f"Bearer {eng_token}"})
            assert resp_eng.status_code == 200


@pytest.mark.asyncio
async def test_dashboard_kpi_and_mttr_calculation():
    """Kiểm tra tính toán MTTR trung bình (10 phút và 20 phút -> 15.0 phút) và Top mã lỗi."""
    created_ticket_ids = []
    async with AsyncSessionLocal() as db:
        machine = (await db.execute(select(Machine))).scalars().first()
        assert machine is not None

        now = datetime.now(timezone.utc)
        t1 = IncidentTicket(
            ticket_code=f"KPI-T1-{uuid4().hex[:6]}",
            machine_id=machine.id,
            error_code="E-204",
            description="Test MTTR 10 min",
            priority=TicketPriority.HIGH,
            status=TicketStatus.RESOLVED,
            started_at=now - timedelta(minutes=10),
            resolved_at=now,
        )
        t2 = IncidentTicket(
            ticket_code=f"KPI-T2-{uuid4().hex[:6]}",
            machine_id=machine.id,
            error_code="E-204",
            description="Test MTTR 20 min",
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.CLOSED,
            started_at=now - timedelta(minutes=25),
            resolved_at=now - timedelta(minutes=5),
        )
        db.add_all([t1, t2])
        await db.commit()
        await db.refresh(t1)
        await db.refresh(t2)
        created_ticket_ids = [t1.id, t2.id]

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            eng_token = await _get_token(client, "engineer", "Engineer@2026")

            kpi_resp = await client.get(
                "/api/v1/dashboard/kpi",
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert kpi_resp.status_code == 200
            kpi = kpi_resp.json()
            assert kpi["total_sops"] >= 3
            assert kpi["total_tickets"] >= 2
            assert kpi["resolved_tickets"] >= 2
            assert kpi["mttr_minutes"] == pytest.approx(15.0, abs=0.1)

            charts_resp = await client.get(
                "/api/v1/dashboard/charts",
                headers={"Authorization": f"Bearer {eng_token}"},
            )
            assert charts_resp.status_code == 200
            charts = charts_resp.json()
            assert len(charts["incidents_by_month"]) >= 1
            assert any(item["error_code"] == "E-204" for item in charts["top_error_codes"])
            assert "RESOLVED" in charts["incidents_by_status"]
    finally:
        async with AsyncSessionLocal() as db:
            await db.execute(delete(IncidentTicket).where(IncidentTicket.id.in_(created_ticket_ids)))
            await db.commit()


@pytest.mark.asyncio
async def test_admin_endpoints_rbac_admin_only(monkeypatch):
    """Chỉ Admin mới được phép truy cập /admin/audit_logs và /admin/system_status."""

    class _FakeVS:
        collection_name = "sop_documents"

        def count(self) -> int:
            return 0

    monkeypatch.setattr(admin_router_module, "get_vector_store", lambda: _FakeVS())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        op_token = await _get_token(client, "operator", "Operator@2026")
        eng_token = await _get_token(client, "engineer", "Engineer@2026")
        mgr_token = await _get_token(client, "manager", "Manager@2026")
        admin_token = await _get_token(client, "admin", "Admin@2026")

        for tok in (op_token, eng_token, mgr_token):
            r_logs = await client.get("/api/v1/admin/audit_logs", headers={"Authorization": f"Bearer {tok}"})
            r_stat = await client.get("/api/v1/admin/system_status", headers={"Authorization": f"Bearer {tok}"})
            assert r_logs.status_code == 403
            assert r_stat.status_code == 403

        assert (await client.get("/api/v1/admin/audit_logs", headers={"Authorization": f"Bearer {admin_token}"})).status_code == 200
        assert (await client.get("/api/v1/admin/system_status", headers={"Authorization": f"Bearer {admin_token}"})).status_code == 200


@pytest.mark.asyncio
async def test_admin_system_status_and_audit_logs_filtering(monkeypatch):
    """Kiểm tra lọc audit_logs theo is_refused=true và thông số tổng hợp trong system_status."""

    class _FakeVS:
        collection_name = "sop_documents"

        def count(self) -> int:
            return 42

    monkeypatch.setattr(admin_router_module, "get_vector_store", lambda: _FakeVS())

    created_log_ids = []
    async with AsyncSessionLocal() as db:
        log_ok = ChatAuditLog(
            question="Lỗi E-204 xử lý sao?",
            answer="Nhấn nút Pause và gỡ băng bị kẹt.",
            cited_doc_ids=["doc-1"],
            cited_pages=[1],
            top_score=0.91,
            is_refused=False,
            ttft_ms=120,
            latency_ms=450,
            is_partial=False,
        )
        log_refused = ChatAuditLog(
            question="Cách thay nhớt xe máy?",
            answer="Quy trình hiện tại chưa ghi nhận...",
            cited_doc_ids=[],
            cited_pages=[],
            top_score=0.12,
            is_refused=True,
            ttft_ms=15,
            latency_ms=20,
            is_partial=False,
        )
        db.add_all([log_ok, log_refused])
        await db.commit()
        await db.refresh(log_ok)
        await db.refresh(log_refused)
        created_log_ids = [log_ok.id, log_refused.id]

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            admin_token = await _get_token(client, "admin", "Admin@2026")

            logs_resp = await client.get(
                "/api/v1/admin/audit_logs?is_refused=true",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert logs_resp.status_code == 200
            logs_body = logs_resp.json()
            assert logs_body["total"] >= 1
            assert all(item["is_refused"] is True for item in logs_body["items"])
            assert any(item["id"] == log_refused.id for item in logs_body["items"])

            stat_resp = await client.get(
                "/api/v1/admin/system_status",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert stat_resp.status_code == 200
            stat = stat_resp.json()
            assert stat["status"] == "ok"
            assert stat["database"]["status"] == "ok"
            assert stat["vector_store"]["vector_count"] == 42
            assert "llm" in stat
            assert stat["counts"]["chat_audit_logs"] >= 2
    finally:
        async with AsyncSessionLocal() as db:
            await db.execute(delete(ChatAuditLog).where(ChatAuditLog.id.in_(created_log_ids)))
            await db.commit()
