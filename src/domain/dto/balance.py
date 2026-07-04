from decimal import Decimal
from typing import Annotated

from pydantic import Field, BaseModel

from src.domain.entities.enums import TransactionType, TransactionDirection

Balance = Annotated[
    Decimal,
    Field(ge=0, decimal_places=2),
]


class BalanceDTO(BaseModel):
    balance: Balance


class BalanceChangeRequestDTO(BaseModel):
    amount: Balance


class BalanceAdminChangeRequestDTO(BalanceChangeRequestDTO):
    user_id: int
    direction: TransactionDirection


class BalanceChangeDTO(BalanceAdminChangeRequestDTO):
    reason: TransactionType


class BalanceOperationResultDTO(BalanceChangeDTO, BalanceDTO):
    pass


class InternalBalanceOperationResultDTO(BalanceOperationResultDTO):
    transaction_id: int
