from enum import StrEnum


class CodeStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"  # Закончился срок действия
    DEPLETED = "depleted"  # Активирован максимальное количество раз
    REVOKED = "revoked"


class TransactionDirection(StrEnum):
    CREDIT = "CREDIT"  # Пополнение
    DEBIT = "DEBIT"  # Списание


class TransactionType(StrEnum):
    GAME = "game"
    CODE_REDEEM = "code_redeem"
    ADMIN_ADJUST = "admin_adjust"
    WITHDRAW = "withdraw"


class GameResult(StrEnum):
    WIN = "win"
    LOSE = "lose"


class GameBetType(StrEnum):
    OVER = "over"
    UNDER = "under"
