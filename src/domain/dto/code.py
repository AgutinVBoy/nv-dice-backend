from pydantic import BaseModel, Field, ConfigDict

from src.domain.dto.balance import Balance
from src.domain.dto.common import CustomDateTime, UppercaseStr
from src.domain.entities.enums import CodeStatus


class CodeBaseDTO(BaseModel):
    code: UppercaseStr = Field(min_length=3, max_length=255)
    amount: Balance = Field(gt=0)
    status: CodeStatus = CodeStatus.ACTIVE
    max_uses: int = Field(gt=0, default=1)
    uses_count: int = Field(ge=0, default=0)
    max_uses_per_user: int = Field(gt=0, default=1)
    starts_at: CustomDateTime | None = None
    expires_at: CustomDateTime | None = None


class CodeCreateDTO(CodeBaseDTO):
    pass


class CodePatchDTO(BaseModel):
    code: UppercaseStr | None = Field(min_length=3, max_length=255, default=None)
    amount: Balance | None = Field(gt=0, default=None)
    status: CodeStatus | None = None
    max_uses: int | None = Field(gt=0, default=None)
    uses_count: int | None = Field(ge=0, default=None)
    max_uses_per_user: int | None = Field(gt=0, default=None)
    starts_at: CustomDateTime | None = None
    expires_at: CustomDateTime | None = None


class CodeDTO(CodeBaseDTO):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: CustomDateTime
    updated_at: CustomDateTime | None
    created_by_id: int | None
    updated_by_id: int | None
