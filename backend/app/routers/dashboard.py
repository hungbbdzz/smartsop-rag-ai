from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import UserRole
from app.services.dashboard_service import get_dashboard_charts, get_dashboard_kpi

# Chỉ Kỹ sư ca, Quản đốc và Admin được xem Dashboard KPI vận hành
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard & KPI"],
    dependencies=[
        Depends(require_roles([UserRole.SHIFT_ENGINEER, UserRole.FACTORY_MANAGER, UserRole.ADMIN]))
    ],
)


@router.get(
    "/kpi",
    summary="Lấy các chỉ số KPI tổng quan nhà máy (SOP, Sự cố, MTTR, RAG Latency)",
)
async def read_dashboard_kpi(db: AsyncSession = Depends(get_db)):
    return await get_dashboard_kpi(db)


@router.get(
    "/charts",
    summary="Lấy dữ liệu thống kê biểu đồ theo tháng, Top mã lỗi & Top SOP trích dẫn",
)
async def read_dashboard_charts(db: AsyncSession = Depends(get_db)):
    return await get_dashboard_charts(db)
