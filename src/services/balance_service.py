from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ApiError
from src.core.i18n import t
from src.domain.dto.balance import BalanceChangeDTO, InternalBalanceOperationResultDTO
from src.domain.entities.enums import TransactionDirection
from src.domain.entities.models import UserBalance, BalanceTransaction
from src.domain.interfaces.balance_service import IBalanceService


class BalanceService(IBalanceService):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_balance(self, data: BalanceChangeDTO, auto_commit: bool = True) -> InternalBalanceOperationResultDTO:
        user_balance_query = await self.session.execute(
            select(UserBalance).where(UserBalance.user_id == data.user_id).with_for_update()
        )
        user_balance: UserBalance = user_balance_query.scalar_one_or_none()
        if not user_balance:
            raise ApiError.not_found(t("ERR_USER_NOT_FOUND", user_id=data.user_id))

        match data.direction:
            case TransactionDirection.CREDIT:
                new_balance = user_balance.balance + data.amount
            case TransactionDirection.DEBIT:
                new_balance = user_balance.balance - data.amount
                if new_balance < 0:
                    raise ApiError.conflict(t("ERR_BALANCE_NOT_ENOUGH"))
            case _:
                raise RuntimeError(f"Unknown TransactionDirection: {data.direction}")


        user_balance.balance = new_balance

        transaction = BalanceTransaction(
            user_id=data.user_id,
            transaction_type=data.reason,
            amount=data.amount,
            new_balance=new_balance
        )
        self.session.add(transaction)
        await self.session.flush()

        if auto_commit:
            await self.session.commit()

        return InternalBalanceOperationResultDTO.model_copy(
            data,
            update={
                "transaction_id": transaction.id,
                "balance": new_balance,
            }
        )
