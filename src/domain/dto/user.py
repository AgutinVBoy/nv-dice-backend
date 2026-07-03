from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator, Field

from src.domain.dto.common import StrongPassword
from src.domain.dto.role import RoleDTO


class UserBaseDTO(BaseModel):
    username: str = Field(min_length=5, max_length=30)

    @field_validator('username', mode='after')
    @classmethod
    def to_lowercase(cls, v: str) -> str:
        return v.lower()


class UserCreateDTO(UserBaseDTO):
    password: StrongPassword


class UserResponseDTO(UserBaseDTO):
    id: int
    role: RoleDTO


class UserBalanceDTO(UserResponseDTO):
    balance: Decimal


class UserAdminResponseDTO(UserBalanceDTO):
    is_active: bool
    registered_at: datetime
    password_updated_at: datetime
