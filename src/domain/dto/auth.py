from pydantic import BaseModel

from src.domain.dto.common import Password, StrongPassword
from src.domain.dto.user import UserBaseDTO


class LoginDTO(UserBaseDTO):
    password: Password


class RefreshTokenDTO(BaseModel):
    refresh_token: str


class ChangePasswordDTO(BaseModel):
    old_password: Password
    new_password: StrongPassword


class TokenResponseDTO(BaseModel):
    access_token: str
    refresh_token: str
    access_token_expires_in: int
    refresh_token_expires_in: int
    token_type: str = "Bearer"
