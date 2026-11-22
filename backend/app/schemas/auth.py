from typing import Optional
from pydantic import BaseModel
from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """Payload người dùng gửi lên khi đăng nhập."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Dữ liệu trả về khi đăng nhập thành công."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Số giây token có hiệu lực (ví dụ 28800 giây = 8 tiếng)
    user: UserResponse


class TokenPayload(BaseModel):
    """Cấu trúc dữ liệu mã hóa bên trong JWT token."""
    sub: str  # user id
    username: Optional[str] = None
    role: Optional[str] = None

