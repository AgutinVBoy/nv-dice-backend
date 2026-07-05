from dishka import FromDishka
from fastapi import Request

from src.domain.dto.code import CodeCreateDTO, CodeDTO
from src.domain.interfaces.code_service import ICodeService


async def create_code(
        *,
        code_service: FromDishka[ICodeService],
        body: CodeCreateDTO,
        request: Request
) -> CodeDTO:
    return await code_service.create_code(request.state.current_user, body)
