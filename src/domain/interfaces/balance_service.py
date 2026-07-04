from abc import ABC, abstractmethod

from src.domain.dto.balance import BalanceChangeDTO, InternalBalanceOperationResultDTO


class IBalanceService(ABC):
    @abstractmethod
    async def update_balance(self, data: BalanceChangeDTO, auto_commit: bool = True) -> InternalBalanceOperationResultDTO:
        ...
