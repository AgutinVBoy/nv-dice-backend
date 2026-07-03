from datetime import timezone

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import ApiError
from src.core.i18n import t
from src.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    validate_refresh_token,
)
from src.domain.dto.auth import LoginDTO, TokenResponseDTO, RefreshTokenDTO, ChangePasswordDTO
from src.domain.dto.user import UserCreateDTO
from src.domain.entities.models import User, UserBalance
from src.domain.interfaces.auth_service import IAuthService
from src.domain.interfaces.user_repo import IUserRepository


def _generate_tokens(user_id: int) -> TokenResponseDTO:
    return TokenResponseDTO(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
        access_token_expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


class AuthService(IAuthService):
    def __init__(self, user_repo: IUserRepository, session: AsyncSession):
        self.user_repo = user_repo
        self.session = session

    async def login(self, data: LoginDTO) -> TokenResponseDTO:
        user = await self.user_repo.get_by_username(data.username)

        if not user or not verify_password(data.password, user.password):
            raise ApiError.unauthorized(t("ERR_INVALID_CREDENTIALS"))

        if not user.is_active:
            raise ApiError.unauthorized(t("ERR_USER_INACTIVE"))

        return _generate_tokens(user.id)

    async def register(self, data: UserCreateDTO) -> TokenResponseDTO:
        existing = await self.user_repo.get_by_username(data.username)
        if existing:
            raise ApiError.conflict(t("ERR_USERNAME_ALREADY_EXISTS"))

        user = User(username=data.username, password=hash_password(data.password))
        user = await self.user_repo.create(user)
        await self.session.merge(UserBalance(user_id=user.id))

        await self.session.commit()
        return _generate_tokens(user.id)

    async def refresh(self, data: RefreshTokenDTO) -> TokenResponseDTO:
        payload = validate_refresh_token(data.refresh_token)
        if not payload:
            raise ApiError.unauthorized(t("ERR_INVALID_REFRESH_TOKEN"))

        user = await self.user_repo.get_by_id(payload.user_id)
        if not user or not user.is_active:
            raise ApiError.unauthorized(t("ERR_UNAUTHORIZED"))

        pwd_ts = user.password_updated_at.replace(tzinfo=timezone.utc)
        if payload.iat < pwd_ts:
            raise ApiError.unauthorized(t("ERR_TOKEN_REVOKED"))

        return _generate_tokens(user.id)

    async def change_password(
        self, user_id: int, data: ChangePasswordDTO
    ) -> TokenResponseDTO:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ApiError.not_found(t("ERR_USER_NOT_FOUND", user_id=user_id))

        if not verify_password(data.old_password, user.password):
            raise ApiError.unauthorized(t("ERR_INVALID_OLD_PASSWORD"))

        user.password = hash_password(data.new_password)
        user.password_updated_at = func.now()
        await self.user_repo.update(user)
        await self.session.commit()

        return _generate_tokens(user.id)