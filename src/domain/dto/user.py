from datetime import datetime

from pydantic import BaseModel, field_validator, Field, ConfigDict, AliasPath

from src.domain.dto.balance import Balance
from src.domain.dto.common import StrongPassword
from src.domain.dto.role import RoleDTO


class UserBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(min_length=5, max_length=30)

    @field_validator('username', mode='after')
    @classmethod
    def to_lowercase(cls, v: str) -> str:
        return v.lower()


class UserCreateDTO(UserBaseDTO):
    password: StrongPassword


class UserResponseDTO(UserBaseDTO):
    id: int
    role: RoleDTO = Field(validation_alias="role_ref")


class UserBalanceDTO(UserResponseDTO):
    balance: Balance = Field(validation_alias=AliasPath("balance_ref", "balance"))


class UserAdminResponseDTO(UserBalanceDTO):
    is_active: bool
    registered_at: datetime
    password_updated_at: datetime
