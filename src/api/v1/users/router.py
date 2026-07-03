from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends

from src.core.i18n import t
from . import handlers
from ...dependencies.rbac import require_admin

user_router = APIRouter(route_class=DishkaRoute)

user_router.add_api_route(
    path="/me",
    endpoint=handlers.get_me,
    methods=["GET"],
    summary=t("API_GET_ME"),
)

user_router.add_api_route(
    path="/{user_id}",
    endpoint=handlers.get_user,
    methods=["GET"],
    summary=t("API_GET_USER"),
    dependencies=[Depends(require_admin())],
)
