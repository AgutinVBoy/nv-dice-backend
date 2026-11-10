from dishka import FromDishka
from fastapi import Path, Query, Request

from src.api.dependencies.rbac import require_admin
from src.core.i18n import t
from src.domain.dto.game import (
    GameHashDTO, GameBetDTO, GameResponseDTO, GameHistoryDTO, GameResultDTO
)
from src.domain.interfaces.game_service import IGameService


async def get_game_history(
        *,
        game_service: FromDishka[IGameService],
        request: Request,
        page: int = Query(1, ge=1, description=t("DESC_PAGE")),
        per_page: int = Query(20, ge=1, le=100, description=t("DESC_PER_PAGE")),
        user_id: int | None = Query(None, ge=1, description=t("DESC_GAME_HISTORY_USER_ID")),
) -> GameHistoryDTO:
    if user_id is not None:
        await require_admin(request)
    else:
        user_id = request.state.current_user
    return await game_service.get_game_history(user_id, page, per_page)


async def get_game_by_id(
        *,
        game_service: FromDishka[IGameService],
        request: Request,
        game_id: int = Path(..., ge=1, description=t("DESC_GAME_ID")),
) -> GameResultDTO:
    return await game_service.get_game_by_id(
        request.state.current_user, game_id, is_admin=request.state.is_admin
    )


async def init_game(
        *,
        game_service: FromDishka[IGameService],
        request: Request
) -> GameHashDTO:
    return await game_service.get_or_init_game(request.state.current_user)


async def process_game(
        *,
        game_service: FromDishka[IGameService],
        body: GameBetDTO,
        request: Request
) -> GameResponseDTO:
    return await game_service.process_game(request.state.current_user, body)
