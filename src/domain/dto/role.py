from pydantic import BaseModel


class RoleDTO(BaseModel):
    code: str
    label: str
