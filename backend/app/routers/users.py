from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, UserUpdate

# Toàn bộ nhóm API quản lý tài khoản đều được bảo vệ nghiêm ngặt: CHỈ ADMIN MỚI ĐƯỢC PHÉP
router = APIRouter(
    prefix="/users",
    tags=["User Management"],
    dependencies=[Depends(require_roles([UserRole.ADMIN]))],
)


@router.get(
    "",
    response_model=List[UserResponse],
    summary="Xem danh sách nhân sự (Hỗ trợ lọc theo Role và trạng thái hoạt động)",
)
async def list_users(
    role: Optional[UserRole] = Query(None, description="Lọc theo vai trò (ADMIN, FACTORY_MANAGER, SHIFT_ENGINEER, OPERATOR)"),
    is_active: Optional[bool] = Query(None, description="Lọc theo trạng thái tài khoản (True/False)"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)

    stmt = stmt.order_by(User.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Xem chi tiết thông tin một tài khoản nhân sự",
)
async def get_user_detail(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy tài khoản với ID '{user_id}'",
        )
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới một tài khoản nhân sự trong nhà máy",
)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    # 1. Kiểm tra username đã tồn tại chưa
    username_stmt = select(User).where(User.username == user_in.username)
    username_res = await db.execute(username_stmt)
    if username_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tên đăng nhập '{user_in.username}' đã được sử dụng",
        )

    # 2. Kiểm tra email đã tồn tại chưa
    email_stmt = select(User).where(User.email == user_in.email)
    email_res = await db.execute(email_stmt)
    if email_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Địa chỉ email '{user_in.email}' đã được sử dụng",
        )

    # 3. Tạo tài khoản với mật khẩu băm Bcrypt
    user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=user_in.is_active,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Cập nhật thông tin nhân viên, đổi vai trò hoặc khóa tài khoản",
)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy tài khoản với ID '{user_id}'",
        )

    # Nếu đổi email, kiểm tra trùng lặp
    if user_in.email and user_in.email != user.email:
        email_stmt = select(User).where(User.email == user_in.email)
        email_res = await db.execute(email_stmt)
        if email_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Địa chỉ email '{user_in.email}' đã được sử dụng",
            )

    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        user.password_hash = hash_password(update_data.pop("password"))

    for field, val in update_data.items():
        setattr(user, field, val)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa tài khoản nhân viên",
)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_active_user),
):
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quản trị viên không thể tự xóa tài khoản của chính mình",
        )

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy tài khoản với ID '{user_id}'",
        )

    await db.delete(user)
    await db.commit()
    return {"message": f"Đã xóa thành công tài khoản '{user.username}'"}

