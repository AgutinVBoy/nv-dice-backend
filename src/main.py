import logging

import uvicorn
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from src.api.middlewares.auth import JWTAuthMiddleware, PUBLIC_PATHS
from src.core.config import settings
from src.core.exceptions import setup_exception_handlers
from src.core.ioc import DatabaseProvider
from src.core.logger import get_log_config
from src.core.openapi import setup_openapi_bearer_auth

logger = logging.getLogger(__name__)

MIDDLEWARES = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
    Middleware(JWTAuthMiddleware),
]

ROUTERS = [
]


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.app_version,
        middleware=MIDDLEWARES,
    )

    container = make_async_container(
        DatabaseProvider(),
    )
    setup_dishka(container, app)

    setup_exception_handlers(app)

    for router, prefix in ROUTERS:
        app.include_router(router, prefix=prefix)

    setup_openapi_bearer_auth(app, PUBLIC_PATHS)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=8000, reload=False, log_config=get_log_config()
    )
