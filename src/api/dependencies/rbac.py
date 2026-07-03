from fastapi import Request

from src.core.exceptions import ApiError


def require_admin():
    async def _check_role(request: Request) -> None:
        if not request.state.is_admin:
            raise ApiError.forbidden()

    return _check_role
