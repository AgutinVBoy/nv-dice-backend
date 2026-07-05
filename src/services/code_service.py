from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from src.core.exceptions import ApiError
from src.core.i18n import t
from src.domain.dto.code import CodeDTO, CodeCreateDTO, CodePatchDTO
from src.domain.entities.models import Code
from src.domain.interfaces.code_service import ICodeService


class CodeService(ICodeService):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_code(self, user_id: int, data: CodeCreateDTO) -> CodeDTO:
        if await self.session.scalar(select(exists().where(Code.code == data.code))):
            raise ApiError.conflict(t("ERR_CODE_ALREADY_EXISTS"))

        code = Code(
            code=data.code,
            amount=data.amount,
            status=data.status,
            max_uses=data.max_uses,
            uses_count=data.uses_count,
            max_uses_per_user=data.max_uses_per_user,
            starts_at=data.starts_at,
            expires_at=data.expires_at,
            created_by_id=user_id
        )
        self.session.add(code)
        await self.session.commit()
        return CodeDTO.model_validate(code)

    async def update_code(self, user_id: int, code_id: int, data: CodeCreateDTO | CodePatchDTO) -> CodeDTO:
        pass

    async def delete_code(self, user_id: int, code_id: int) -> CodeDTO:
        pass

    async def redeem_code(self, user_id: int, code: str):
        pass
