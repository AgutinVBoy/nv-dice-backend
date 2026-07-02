from enum import StrEnum


class CodeStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"  # Закончился срок действия
    DEPLETED = "depleted"  # Активирован максимальное количество раз
    REVOKED = "revoked"
