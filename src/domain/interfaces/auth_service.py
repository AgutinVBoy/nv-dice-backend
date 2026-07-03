from abc import ABC, abstractmethod

from src.domain.dto.auth import (
    ChangePasswordDTO,
    LoginDTO,
    RefreshTokenDTO,
    TokenResponseDTO,
)
from src.domain.dto.user import UserCreateDTO


class IAuthService(ABC):
    @abstractmethod
    async def login(self, data: LoginDTO) -> TokenResponseDTO:
        ...

    @abstractmethod
    async def register(self, data: UserCreateDTO) -> TokenResponseDTO:
        ...

    @abstractmethod
    async def refresh(self, data: RefreshTokenDTO) -> TokenResponseDTO:
        ...

    @abstractmethod
    async def change_password(self, user_id: int, data: ChangePasswordDTO) -> TokenResponseDTO:
        ...
