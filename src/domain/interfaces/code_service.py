from abc import ABC, abstractmethod

from src.domain.dto.code import CodeDTO, CodeCreateDTO, CodePatchDTO


class ICodeService(ABC):
    @abstractmethod
    async def create_code(self, user_id: int, data: CodeCreateDTO) -> CodeDTO:
        ...

    @abstractmethod
    async def update_code(self, user_id: int, code_id: int, data: CodeCreateDTO | CodePatchDTO) -> CodeDTO:
        ...

    @abstractmethod
    async def delete_code(self, user_id: int, code_id: int) -> CodeDTO:
        ...

    @abstractmethod
    async def redeem_code(self, user_id: int, code: str):
        ...
