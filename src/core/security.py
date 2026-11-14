import typing as tp
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
import jwt

from src.core.config import settings

DEFAULT_ENCODING = "utf-8"


@dataclass(frozen=True)
class TokenPayload:
    user_id: int
    token_version: UUID


def _create_token(
    user_id: int | str,
    token_type: str,
    expires_delta: timedelta,
    token_version: UUID,
) -> str:
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + expires_delta,
        "type": token_type,
        "ver": str(token_version),
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def _validate_token(token: str, expected_type: str) -> tp.Optional[TokenPayload]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != expected_type:
            return None
        sub = payload.get("sub")
        if not sub:
            return None
        if not (token_version := payload.get("ver")) or not isinstance(token_version, str):
            return None
        return TokenPayload(user_id=int(sub), token_version=UUID(token_version))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError, KeyError):
        return None


def create_access_token(user_id: int | str, token_version: UUID) -> str:
    return _create_token(
        user_id,
        "access",
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_version,
    )


def create_refresh_token(user_id: int | str, token_version: UUID) -> str:
    return _create_token(
        user_id,
        "refresh",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_version,
    )


def validate_access_token(token: str) -> tp.Optional[TokenPayload]:
    return _validate_token(token, "access")


def validate_refresh_token(token: str) -> tp.Optional[TokenPayload]:
    return _validate_token(token, "refresh")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(DEFAULT_ENCODING), salt)
    return hashed.decode(DEFAULT_ENCODING)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode(DEFAULT_ENCODING), hashed_password.encode(DEFAULT_ENCODING)
    )
