from pydantic import BaseModel


class UserBaseDTO(BaseModel):
    username: str


class UserCreateDTO(UserBaseDTO):
    password: str
