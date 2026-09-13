from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends

from src.api.dependencies.rbac import require_admin
from src.core.i18n import t
from . import handlers

balance_router = APIRouter(route_class=DishkaRoute)

balance_router.add_api_route(
    path="/modify",
    endpoint=handlers.modify_balance,
    methods=["POST"],
    summary=t("API_MODIFY_BALANCE"),
    dependencies=[Depends(require_admin)],
)

balance_router.add_api_route(
    path="/withdraw",
    endpoint=handlers.withdraw,
    methods=["POST"],
    summary=t("API_WITHDRAW"),
)
