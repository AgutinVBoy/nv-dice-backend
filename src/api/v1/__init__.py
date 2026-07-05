from fastapi import APIRouter

from src.core.i18n import t
from .auth.router import auth_router
from .balance.routers import balance_router
from .code.routers import code_router
from .users.router import user_router

v1_router = APIRouter()

v1_router.include_router(auth_router, prefix="/auth", tags=[t("AUTH_LABEL")])
v1_router.include_router(balance_router, prefix="/balance", tags=[t("BALANCE_LABEL")])
v1_router.include_router(code_router, prefix="/code", tags=[t("CODE_LABEL")])
v1_router.include_router(user_router, prefix="/users", tags=[t("USERS_LABEL")])
