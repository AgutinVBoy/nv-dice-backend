from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from src.core.i18n import t
from . import handlers

auth_router = APIRouter(route_class=DishkaRoute)

auth_router.add_api_route(
    path="/login",
    endpoint=handlers.login,
    methods=["POST"],
    summary=t("API_LOGIN"),
)

auth_router.add_api_route(
    path="/register",
    endpoint=handlers.register,
    methods=["POST"],
    summary=t("API_REGISTER"),
)

auth_router.add_api_route(
    path="/refresh",
    endpoint=handlers.refresh,
    methods=["POST"],
    summary=t("API_REFRESH"),
)

auth_router.add_api_route(
    path="/change-password",
    endpoint=handlers.change_password,
    methods=["POST"],
    summary=t("API_CHANGE_PASSWORD"),
)
