from fastapi import APIRouter

from .auth.router import auth_router
from .users.router import user_router

v1_router = APIRouter()

v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
v1_router.include_router(user_router, prefix="/users", tags=["users"])
