from dishka import FromDishka
from fastapi import Request

from src.domain.dto.balance import (
    BalanceChangeRequestDTO,
    BalanceOperationResultDTO,
    BalanceChangeDTO,
    BalanceAdminChangeRequestDTO,
)
from src.domain.entities.enums import TransactionDirection, TransactionType
from src.domain.interfaces.balance_service import IBalanceService


async def withdraw(
        *,
        balance_service: FromDishka[IBalanceService],
        body: BalanceChangeRequestDTO,
        request: Request
) -> BalanceOperationResultDTO:
    data = BalanceChangeDTO(
        user_id=request.state.current_user,
        direction=TransactionDirection.DEBIT,
        reason=TransactionType.WITHDRAW,
        amount=body.amount
    )
    result = await balance_service.update_balance(data)
    return BalanceOperationResultDTO.model_copy(result)


async def modify_balance(
        *,
        balance_service: FromDishka[IBalanceService],
        body: BalanceAdminChangeRequestDTO,
        request: Request
) -> BalanceOperationResultDTO:
    data = BalanceChangeDTO.model_copy(body, update={"reason": TransactionType.ADMIN_ADJUST})
    result = await balance_service.update_balance(data)
    return BalanceOperationResultDTO.model_copy(result)
