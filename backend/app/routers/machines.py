from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.models.machine import Machine, MachineStatus
from app.models.production_line import ProductionLine
from app.models.user import User, UserRole
from app.schemas.machine import MachineCreate, MachineResponse, MachineUpdate

router = APIRouter(prefix="/machines", tags=["Machines"])


@router.get(
    "",
    response_model=List[MachineResponse],
    summary="Lấy danh sách máy móc (hỗ trợ lọc theo dây chuyền và trạng thái)",
)
async def list_machines(
    line_id: Optional[str] = Query(None, description="Lọc theo ID dây chuyền sản xuất"),
    status: Optional[MachineStatus] = Query(None, description="Lọc theo trạng thái máy (OPERATIONAL, MAINTENANCE, ERROR)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mọi người dùng đã đăng nhập đều có thể tra cứu danh sách máy."""
    stmt = select(Machine)
    if line_id:
        stmt = stmt.where(Machine.line_id == line_id)
    if status:
        stmt = stmt.where(Machine.status == status)

    stmt = stmt.order_by(Machine.machine_code.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/{machine_id}",
    response_model=MachineResponse,
    summary="Xem thông tin chi tiết một máy móc",
)
async def get_machine(
    machine_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    stmt = select(Machine).where(Machine.id == machine_id)
    result = await db.execute(stmt)
    machine = result.scalar_one_or_none()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy thiết bị máy với ID '{machine_id}'",
        )
    return machine


@router.post(
    "",
    response_model=MachineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm mới một máy móc vào dây chuyền",
)
async def create_machine(
    machine_in: MachineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.FACTORY_MANAGER])),
):
    """Chỉ Quản trị viên (Admin) hoặc Quản đốc (Factory Manager) mới có quyền thêm máy."""
    # 1. Kiểm tra dây chuyền có tồn tại không
    line_stmt = select(ProductionLine).where(ProductionLine.id == machine_in.line_id)
    line_result = await db.execute(line_stmt)
    if not line_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dây chuyền với ID '{machine_in.line_id}' không tồn tại",
        )

    # 2. Kiểm tra trùng mã máy (machine_code)
    code_stmt = select(Machine).where(Machine.machine_code == machine_in.machine_code)
    code_result = await db.execute(code_stmt)
    if code_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã máy '{machine_in.machine_code}' đã tồn tại trong hệ thống",
        )

    machine = Machine(
        machine_code=machine_in.machine_code,
        name=machine_in.name,
        model=machine_in.model,
        manufacturer=machine_in.manufacturer,
        status=machine_in.status,
        line_id=machine_in.line_id,
    )
    db.add(machine)
    await db.commit()
    await db.refresh(machine)
    return machine


@router.patch(
    "/{machine_id}",
    response_model=MachineResponse,
    summary="Cập nhật thông tin hoặc trạng thái máy móc",
)
async def update_machine(
    machine_id: str,
    machine_in: MachineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.ADMIN, UserRole.FACTORY_MANAGER, UserRole.SHIFT_ENGINEER])
    ),
):
    """Admin, Quản đốc hoặc Kỹ sư ca trực có quyền cập nhật trạng thái máy."""
    stmt = select(Machine).where(Machine.id == machine_id)
    result = await db.execute(stmt)
    machine = result.scalar_one_or_none()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy thiết bị máy với ID '{machine_id}'",
        )

    # Nếu đổi dây chuyền, kiểm tra dây chuyền mới có tồn tại không
    if machine_in.line_id and machine_in.line_id != machine.line_id:
        line_stmt = select(ProductionLine).where(ProductionLine.id == machine_in.line_id)
        line_res = await db.execute(line_stmt)
        if not line_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dây chuyền mới với ID '{machine_in.line_id}' không tồn tại",
            )

    update_data = machine_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(machine, field, val)

    await db.commit()
    await db.refresh(machine)
    return machine


@router.delete(
    "/{machine_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa máy móc khỏi hệ thống",
)
async def delete_machine(
    machine_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """CHỈ DUY NHẤT ADMIN mới có quyền xóa thiết bị máy móc."""
    stmt = select(Machine).where(Machine.id == machine_id)
    result = await db.execute(stmt)
    machine = result.scalar_one_or_none()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy thiết bị máy với ID '{machine_id}'",
        )

    await db.delete(machine)
    await db.commit()
    return {"message": f"Đã xóa thành công máy '{machine.name}' ({machine.machine_code})"}

