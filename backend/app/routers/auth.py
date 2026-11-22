from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Đăng nhập tài khoản và nhận JWT Access Token",
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Xác thực tài khoản bằng username và password.
    Trả về Access Token (thời hạn 8 tiếng cho 1 ca làm việc nhà máy) cùng thông tin User.
    """
    # 1. Tìm kiếm User theo username
    stmt = select(User).where(User.username == login_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # 2. Kiểm tra mật khẩu bằng Bcrypt
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Kiểm tra trạng thái tài khoản
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa hoặc ngừng hoạt động",
        )

    # 4. Sinh JWT Token với thời hạn cấu hình (mặc định 480 phút = 8 giờ)
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_payload = {
        "sub": user.id,
        "username": user.username,
        "role": user.role.value,
    }
    access_token = create_access_token(data=token_payload, expires_delta=expires_delta)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Lấy thông tin tài khoản đang đăng nhập hiện tại",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Trả về thông tin chi tiết của người dùng gắn với Access Token hiện tại."""
    return UserResponse.model_validate(current_user)

