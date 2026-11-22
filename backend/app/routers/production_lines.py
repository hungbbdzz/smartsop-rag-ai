from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.production_line import ProductionLine
from app.models.user import User, UserRole
from app.schemas.production_line import (
    ProductionLineCreate,
    ProductionLineResponse,
    ProductionLineUpdate,
)

router = APIRouter(prefix="/production-lines", tags=["Production Lines"])


@router.get(
    "",
    response_model=List[ProductionLineResponse],
    summary="Lấy danh sách tất cả các dây chuyền sản xuất",
)
async def list_production_lines(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mọi người dùng đã đăng nhập đều có thể xem danh sách dây chuyền."""
    stmt = select(ProductionLine).order_by(ProductionLine.name.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/{line_id}",
    response_model=ProductionLineResponse,
    summary="Lấy thông tin chi tiết một dây chuyền sản xuất",
)
async def get_production_line(
    line_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    stmt = select(ProductionLine).where(ProductionLine.id == line_id)
    result = await db.execute(stmt)
    line = result.scalar_one_or_none()
    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy dây chuyền với ID '{line_id}'",
        )
    return line


@router.post(
    "",
    response_model=ProductionLineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới một dây chuyền sản xuất",
)
async def create_production_line(
    line_in: ProductionLineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.FACTORY_MANAGER])),
):
    """Chỉ Quản trị viên (Admin) hoặc Quản đốc (Factory Manager) mới có quyền tạo."""
    # Kiểm tra trùng tên
    stmt = select(ProductionLine).where(ProductionLine.name == line_in.name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dây chuyền mang tên '{line_in.name}' đã tồn tại",
        )

    line = ProductionLine(
        name=line_in.name,
        factory_zone=line_in.factory_zone,
        description=line_in.description,
    )
    db.add(line)
    await db.commit()
    await db.refresh(line)
    return line


@router.patch(
    "/{line_id}",
    response_model=ProductionLineResponse,
    summary="Cập nhật thông tin dây chuyền sản xuất",
)
async def update_production_line(
    line_id: str,
    line_in: ProductionLineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.FACTORY_MANAGER])),
):
    stmt = select(ProductionLine).where(ProductionLine.id == line_id)
    result = await db.execute(stmt)
    line = result.scalar_one_or_none()
    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy dây chuyền với ID '{line_id}'",
        )

    # Cập nhật các trường được truyền
    update_data = line_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(line, field, val)

    await db.commit()
    await db.refresh(line)
    return line


@router.delete(
    "/{line_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa một dây chuyền sản xuất",
)
async def delete_production_line(
    line_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """Chỉ ADMIN mới có quyền xóa dây chuyền sản xuất."""
    stmt = select(ProductionLine).where(ProductionLine.id == line_id)
    result = await db.execute(stmt)
    line = result.scalar_one_or_none()
    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy dây chuyền với ID '{line_id}'",
        )

    await db.delete(line)
    await db.commit()
    return {"message": f"Đã xóa thành công dây chuyền '{line.name}'"}

