from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from src.core.i18n import t
from . import handlers

game_router = APIRouter(route_class=DishkaRoute)

game_router.add_api_route(
    path="",
    endpoint=handlers.process_game,
    methods=["POST"],
    summary=t("API_PROCESS_GAME"),
)

game_router.add_api_route(
    path="/history",
    endpoint=handlers.get_game_history,
    methods=["GET"],
    summary=t("API_GET_GAME_HISTORY"),
)

game_router.add_api_route(
    path="/history/{game_id}",
    endpoint=handlers.get_game_by_id,
    methods=["GET"],
    summary=t("API_GET_GAME_BY_ID"),
)

game_router.add_api_route(
    path="/init",
    endpoint=handlers.init_game,
    methods=["POST"],
    summary=t("API_INIT_GAME"),
)
