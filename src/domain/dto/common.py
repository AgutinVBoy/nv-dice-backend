import re
from typing import Annotated

from pydantic import Field, AfterValidator

from src.core.exceptions import ApiError
from src.core.i18n import t


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