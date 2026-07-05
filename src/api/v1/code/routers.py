from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends

from src.api.dependencies.rbac import require_admin
from src.core.i18n import t
from . import handlers

code_router = APIRouter(route_class=DishkaRoute)

code_router.add_api_route(
    path="",
    endpoint=handlers.create_code,
    methods=["POST"],
    summary=t("API_CREATE_CODE"),
    dependencies=[Depends(require_admin())],
)
