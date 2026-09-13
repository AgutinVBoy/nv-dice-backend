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
    dependencies=[Depends(require_admin)],
)

code_router.add_api_route(
    path="/redeem",
    endpoint=handlers.redeem_code,
    methods=["POST"],
    summary=t("API_REDEEM_CODE"),
)

code_router.add_api_route(
    path="/{code_id}",
    endpoint=handlers.get_code_by_id,
    methods=["GET"],
    summary=t("API_GET_CODE"),
    dependencies=[Depends(require_admin)],
)

code_router.add_api_route(
    path="/{code_id}",
    endpoint=handlers.update_code,
    methods=["PUT"],
    summary=t("API_UPDATE_CODE"),
    dependencies=[Depends(require_admin)],
)

code_router.add_api_route(
    path="/{code_id}",
    endpoint=handlers.patch_code,
    methods=["PATCH"],
    summary=t("API_UPDATE_CODE"),
    dependencies=[Depends(require_admin)],
)
