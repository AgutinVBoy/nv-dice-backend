from abc import ABC, abstractmethod

from src.domain.dto.user import UserAdminResponseDTO


class IUserService(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> UserAdminResponseDTO | None:
        ...
