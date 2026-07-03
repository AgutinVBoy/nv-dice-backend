from pydantic import BaseModel

from src.domain.dto.common import StrongPassword
from src.domain.dto.user import UserBaseDTO


class LoginDTO(UserBaseDTO):
    password: str


class RefreshTokenDTO(BaseModel):
    refresh_token: str


class ChangePasswordDTO(BaseModel):
    old_password: str
    new_password: StrongPassword


class TokenResponseDTO(BaseModel):
    access_token: str
    refresh_token: str
    access_token_expires_in: int
    refresh_token_expires_in: int
    token_type: str = "Bearer"
