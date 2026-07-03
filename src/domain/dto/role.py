from pydantic import BaseModel, ConfigDict


class RoleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    label: str
