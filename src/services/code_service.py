from datetime import datetime

from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ApiError, ErrorCollector
from src.core.i18n import t
from src.domain.dto.code import CodeDTO, CodeCreateDTO, CodePatchDTO
from src.domain.dto.common import DATETIME_MASK
from src.domain.entities.enums import CodeStatus
from src.domain.entities.models import Code
from src.domain.interfaces.code_service import ICodeService


class CodeService(ICodeService):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    async def _validate_code(code: Code) -> ErrorCollector:
        errors = ErrorCollector()

        if code.uses_count >= code.max_uses:
            if code.uses_count > code.max_uses:
                errors.add_error("uses_count",
                                 t("ERR_CODE_INVALID_MAX_USES_LESS_THAN_USES_COUNT", max_uses=code.max_uses,
                                   uses_count=code.uses_count))
            if code.status == CodeStatus.ACTIVE:
                errors.add_error("status", t("ERR_CODE_INVALID_USES_COUNT_INCOMPATIBLE_WITH_ACTIVE_STATUS",
                                             uses_count=code.uses_count))

        if code.starts_at and code.expires_at and code.starts_at > code.expires_at:
            errors.add_error("code_validity_period", t("ERR_CODE_INVALID_STARTS_EXPIRES_DATES_INCOMPATIBLE"))

        if code.expires_at and code.status == CodeStatus.ACTIVE and code.expires_at <= datetime.now():
            errors.add_error("code_validity_period", t("ERR_CODE_INVALID_EXPIRES_DATE_INCOMPATIBLE_WITH_ACTIVE_STATUS",
                                                       expires_at=code.expires_at.strftime(DATETIME_MASK)))

        return errors

    async def get_code_by_id(self, code_id: int) -> CodeDTO:
        code: Code = (
            await self.session.execute(select(Code).where(Code.id == code_id).with_for_update())).scalar_one_or_none()
        if not code:
            raise ApiError.not_found(t("ERR_CODE_NOT_FOUND"))
        return CodeDTO.model_validate(code)

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

        errors = await self._validate_code(code)
        if errors.is_error:
            raise ApiError.unprocessable_entity(t("ERR_CODE_INVALID"), details=[errors.errors])

        self.session.add(code)
        await self.session.commit()
        return CodeDTO.model_validate(code)

    async def update_code(self, user_id: int, code_id: int, data: CodeCreateDTO | CodePatchDTO) -> CodeDTO:
        code: Code = (
            await self.session.execute(select(Code).where(Code.id == code_id).with_for_update())).scalar_one_or_none()
        if not code:
            raise ApiError.not_found(t("ERR_CODE_NOT_FOUND"))

        if data.code and data.code != code.code and await self.session.scalar(
                select(exists().where(Code.code == data.code))):
            raise ApiError.conflict(t("ERR_CODE_ALREADY_EXISTS"))

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(code, field, value)
        code.updated_by_id = user_id

        errors = await self._validate_code(code)
        if errors.is_error:
            raise ApiError.unprocessable_entity(t("ERR_CODE_INVALID"), details=[errors.errors])

        await self.session.commit()
        return CodeDTO.model_validate(code)

    async def delete_code(self, user_id: int, code_id: int) -> CodeDTO:
        pass

    async def redeem_code(self, user_id: int, code: str):
        pass
