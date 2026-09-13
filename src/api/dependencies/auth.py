from datetime import timezone

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.exceptions import ApiError
from src.core.i18n import t
from src.core.security import validate_access_token
from src.domain.entities.models import User

bearer_scheme = HTTPBearer(
    bearerFormat="JWT",
    description=t("OPENAPI_BEARER_AUTH_DESCRIPTION"),
    auto_error=False,
)


@inject
async def require_auth(
        request: Request,
        factory: FromDishka[async_sessionmaker[AsyncSession]],
        token_auth: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    if not token_auth:
        raise ApiError.unauthorized(details=[t("ERR_INVALID_TOKEN_FORMAT")])

    token = token_auth.credentials
    payload = validate_access_token(token)
    if not payload:
        raise ApiError.unauthorized()

    async with factory() as session:
        row = (
            await session.execute(
                select(User.is_active, User.password_updated_at, User.role).where(
                    User.id == payload.user_id
                )
            )
        ).one_or_none()

    if not row or not row.is_active:
        raise ApiError.unauthorized()

    pwd_ts = row.password_updated_at.replace(tzinfo=timezone.utc)
    if payload.iat < pwd_ts:
        raise ApiError.unauthorized(t("ERR_TOKEN_REVOKED"))

    request.state.current_user = payload.user_id
    request.state.is_admin = row.role == "admin"
