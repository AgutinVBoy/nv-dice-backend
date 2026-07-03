from pydantic import BaseModel, field_validator, Field

from src.domain.dto.common import StrongPassword


class UserBaseDTO(BaseModel):
    username: str = Field(min_length=5, max_length=30)

    @field_validator('username', mode='after')
    @classmethod
    def to_lowercase(cls, v: str) -> str:
        return v.lower()


class UserCreateDTO(UserBaseDTO):
    password: StrongPassword
