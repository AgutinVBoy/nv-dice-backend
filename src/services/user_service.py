from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ApiError
from src.core.i18n import t
from src.domain.dto.user import UserAdminResponseDTO
from src.domain.interfaces.user_repo import IUserRepository
from src.domain.interfaces.user_service import IUserService


class UserService(IUserService):
    def __init__(self, user_repo: IUserRepository, session: AsyncSession):
        self.user_repo = user_repo
        self.session = session

    async def get_user_by_id(self, user_id: int) -> UserAdminResponseDTO:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ApiError.not_found(t("ERR_USER_NOT_FOUND", user_id=user_id))
        return UserAdminResponseDTO.model_validate(user)
