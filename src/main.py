import logging

import uvicorn
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import v1_router
from src.core.config import settings
from src.core.exceptions import setup_exception_handlers
from src.core.ioc import DatabaseProvider, RepositoryProvider, ServiceProvider, RedisProvider
from src.core.logger import get_log_config

logger = logging.getLogger(__name__)

MIDDLEWARES = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
]

ROUTERS = [
    (v1_router, "/api/v1"),
]


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.app_version,
        middleware=MIDDLEWARES,
    )

    container = make_async_container(
        DatabaseProvider(),
        RedisProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    )
    setup_dishka(container, app)

    setup_exception_handlers(app)

    for router, prefix in ROUTERS:
        app.include_router(router, prefix=prefix)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=8000, reload=False, log_config=get_log_config()
    )
