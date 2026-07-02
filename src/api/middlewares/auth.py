from datetime import timezone

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.i18n import t
from src.core.security import validate_access_token
from src.domain.entities.models import User

PUBLIC_PATHS = [
    "/docs",
    "/openapi.json",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
]


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "error": t("ERR_UNAUTHORIZED"),
                    "details": [t("ERR_INVALID_TOKEN_FORMAT")],
                },
            )

        token = auth_header.split()[-1]
        payload = validate_access_token(token)
        if not payload:
            return JSONResponse(
                status_code=401,
                content={"error": t("ERR_UNAUTHORIZED"), "details": []},
            )

        factory: async_sessionmaker[
            AsyncSession
        ] = await request.app.state.dishka_container.get(
            async_sessionmaker[AsyncSession]
        )
        async with factory() as session:
            row = (
                await session.execute(
                    select(User.is_active, User.password_updated_at).where(
                        User.id == payload.user_id
                    )
                )
            ).one_or_none()

        if not row or not row.is_active:
            return JSONResponse(
                status_code=401,
                content={"error": t("ERR_UNAUTHORIZED"), "details": []},
            )

        pwd_ts = row.password_updated_at.replace(tzinfo=timezone.utc)
        if payload.iat < pwd_ts:
            return JSONResponse(
                status_code=401,
                content={
                    "error": t("ERR_TOKEN_REVOKED"),
                    "details": [],
                },
            )

        request.state.current_user = payload.user_id
        return await call_next(request)
