from pydantic import BaseModel


class LoginDTO(BaseModel):
    username: str
    password: str


class RefreshTokenDTO(BaseModel):
    refresh_token: str


class ChangePasswordDTO(BaseModel):
    old_password: str
    new_password: str


class TokenResponseDTO(BaseModel):
    access_token: str
    refresh_token: str
    access_token_expires_in: int
    refresh_token_expires_in: int
    token_type: str = "Bearer"
