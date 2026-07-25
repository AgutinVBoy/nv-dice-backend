from dishka import FromDishka
from fastapi import Request

from src.domain.dto.game import (
    GameHashDTO
)
from src.domain.interfaces.game_service import IGameService


async def init_game(
        *,
        game_service: FromDishka[IGameService],
        request: Request
) -> GameHashDTO:
    return await game_service.get_or_init_game(request.state.current_user)
