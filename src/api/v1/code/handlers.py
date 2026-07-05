from dishka import FromDishka
from fastapi import Request, Path

from src.core.i18n import t
from src.domain.dto.code import CodeCreateDTO, CodeDTO, CodePatchDTO
from src.domain.interfaces.code_service import ICodeService


async def create_code(
        *,
        code_service: FromDishka[ICodeService],
        body: CodeCreateDTO,
        request: Request
) -> CodeDTO:
    return await code_service.create_code(request.state.current_user, body)


async def update_code(
        *,
        code_service: FromDishka[ICodeService],
        body: CodeCreateDTO,
        code_id: int = Path(..., description=t("DESC_CODE_ID"), ge=1),
        request: Request,
) -> CodeDTO:
    return await code_service.update_code(request.state.current_user, code_id, body)


async def patch_code(
        *,
        code_service: FromDishka[ICodeService],
        body: CodePatchDTO,
        code_id: int = Path(..., description=t("DESC_CODE_ID"), ge=1),
        request: Request,
) -> CodeDTO:
    return await code_service.update_code(request.state.current_user, code_id, body)
