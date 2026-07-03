from dishka.integrations.fastapi import FromDishka
from fastapi import Request

from src.domain.dto.auth import (
    ChangePasswordDTO,
    LoginDTO,
    RefreshTokenDTO,
    TokenResponseDTO,
)
from src.domain.dto.user import UserCreateDTO
from src.domain.interfaces.auth_service import IAuthService


async def login(
    *,
    auth_service: FromDishka[IAuthService],
    body: LoginDTO,
) -> TokenResponseDTO:
    return await auth_service.login(body)


async def register(
    *,
    auth_service: FromDishka[IAuthService],
    body: UserCreateDTO,
) -> TokenResponseDTO:
    return await auth_service.register(body)


async def refresh(
    *,
    auth_service: FromDishka[IAuthService],
    body: RefreshTokenDTO,
) -> TokenResponseDTO:
    return await auth_service.refresh(body)


async def change_password(
    *,
    auth_service: FromDishka[IAuthService],
    body: ChangePasswordDTO,
    request: Request,
) -> TokenResponseDTO:
    user_id: int = request.state.current_user
    return await auth_service.change_password(user_id, body)
