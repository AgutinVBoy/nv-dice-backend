import re
from datetime import datetime
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, Field, AfterValidator, PlainSerializer, BeforeValidator

from src.core.exceptions import ApiError
from src.core.i18n import t

DATETIME_MASK = '%Y-%m-%d %H:%M:%S'
MAX_PASSWORD_BYTES = 72
ItemT = TypeVar("ItemT")


class PaginationDTO(BaseModel, Generic[ItemT]):
    page: int
    per_page: int
    items: list[ItemT]
    has_more: bool


def check_password_byte_length(v: str) -> str:
    if len(v.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise ApiError.unprocessable_entity(
            t("ERR_PASSWORD_TOO_LONG")
        )
    return v


def check_password_strength(v: str) -> str:
    errors = []
    if not any(char.isupper() for char in v):
        errors.append(t("ERR_PASSWORD_NO_UPPERCASE"))
    if not any(char.islower() for char in v):
        errors.append(t("ERR_PASSWORD_NO_LOWERCASE"))
    if not any(char.isdigit() for char in v):
        errors.append(t("ERR_PASSWORD_NO_DIGIT"))
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=`~[\]\\/;']", v):
        errors.append(t("ERR_PASSWORD_NO_SPECIAL"))

    if errors:
        raise ApiError.unprocessable_entity(t("ERR_PASSWORD_IS_WEAK"), errors)
    return v


Password = Annotated[
    str,
    AfterValidator(check_password_byte_length),
]

StrongPassword = Annotated[
    Password,
    Field(min_length=8),
    AfterValidator(check_password_strength)
]

CustomDateTime = Annotated[
    datetime,
    PlainSerializer(lambda dt: dt.strftime(DATETIME_MASK), return_type=str, when_used="json")
]

UppercaseStr = Annotated[
    str,
    BeforeValidator(lambda v: v.upper() if isinstance(v, str) else v)
]