from collections.abc import Sequence

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.core.i18n import t

_OPENAPI_HTTP_METHODS = frozenset(
    {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
)


def setup_openapi_bearer_auth(
    app: FastAPI,
    public_path_prefixes: Sequence[str],
) -> None:
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )
        openapi_schema.setdefault("components", {}).setdefault(
            "securitySchemes", {}
        )["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": t("OPENAPI_BEARER_AUTH_DESCRIPTION"),
        }
        for path, path_item in openapi_schema.get("paths", {}).items():
            is_public = any(path.startswith(p) for p in public_path_prefixes)
            for method, operation in path_item.items():
                if method not in _OPENAPI_HTTP_METHODS:
                    continue
                operation["security"] = (
                    [] if is_public else [{"BearerAuth": []}]
                )
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
