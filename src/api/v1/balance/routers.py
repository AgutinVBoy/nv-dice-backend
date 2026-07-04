from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from src.core.i18n import t
from . import handlers

balance_router = APIRouter(route_class=DishkaRoute)

balance_router.add_api_route(
    path="/withdraw",
    endpoint=handlers.withdraw,
    methods=["POST"],
    summary=t("API_WITHDRAW"),
)
