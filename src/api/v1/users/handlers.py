from dishka import FromDishka
from fastapi import Request, Path

from src.core.i18n import t
from src.domain.dto.user import UserAdminResponseDTO, UserBalanceDTO
from src.domain.interfaces.user_service import IUserService


async def get_me(
    *,
    user_service: FromDishka[IUserService],
    request: Request,
) -> UserBalanceDTO:
    user = await user_service.get_user_by_id(request.state.current_user)
    return UserBalanceDTO.model_validate(user)


async def get_user(
    *,
    user_service: FromDishka[IUserService],
    user_id: int = Path(..., description=t("DESC_USER_ID"), ge=1),
) -> UserAdminResponseDTO:
    return await user_service.get_user_by_id(user_id)
