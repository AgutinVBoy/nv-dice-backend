import re
from datetime import datetime
from typing import Annotated

from pydantic import Field, AfterValidator, PlainSerializer, BeforeValidator

from src.core.exceptions import ApiError
from src.core.i18n import t

DATETIME_MASK = '%Y-%m-%d %H:%M:%S'

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


StrongPassword = Annotated[
    str,
    Field(min_length=8, max_length=128),
    AfterValidator(check_password_strength)
]

CustomDateTime = Annotated[
    datetime,
    PlainSerializer(lambda dt: dt.strftime(DATETIME_MASK), return_type=str)
]

UppercaseStr = Annotated[
    str,
    BeforeValidator(lambda v: v.upper() if isinstance(v, str) else v)
]