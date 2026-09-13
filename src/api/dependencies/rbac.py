from fastapi import Request

from src.core.exceptions import ApiError


async def require_admin(request: Request) -> None:
    if not request.state.is_admin:
        raise ApiError.forbidden()
