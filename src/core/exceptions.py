from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.i18n import t

logger = logging.getLogger(__name__)


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or []

    @classmethod
    def bad_request(cls, message: str | None = None, details: list = None):
        return cls(
            status_code=400, message=message or t("ERR_BAD_REQUEST"), details=details
        )

    @classmethod
    def unauthorized(cls, message: str | None = None, details: list = None):
        return cls(
            status_code=401, message=message or t("ERR_UNAUTHORIZED"), details=details
        )

    @classmethod
    def forbidden(cls, message: str | None = None, details: list = None):
        return cls(
            status_code=403, message=message or t("ERR_FORBIDDEN"), details=details
        )

    @classmethod
    def not_found(cls, message: str | None = None, details: list = None):
        return cls(
            status_code=404, message=message or t("ERR_NOT_FOUND"), details=details
        )

    @classmethod
    def conflict(cls, message: str | None = None, details: list = None):
        return cls(
            status_code=409, message=message or t("ERR_CONFLICT"), details=details
        )

    @classmethod
    def unprocessable_entity(cls, message: str | None = None, details: list = None):
        return cls(
            status_code=422,
            message=message or t("ERR_UNPROCESSABLE_ENTITY"),
            details=details,
        )

    @classmethod
    def bad_gateway(cls, message: str | None = None, details: list = None):
        return cls(
            status_code=502, message=message or t("ERR_BAD_GATEWAY"), details=details
        )


class ErrorCollector:
    def __init__(self, status_code: int = 422):
        self.status_code = status_code
        self.message: str | None = None
        self.errors: dict[str, list[str]] = defaultdict(list)
        self.is_error: bool = False

    def add_error(
        self,
        field_name: str,
        field_error: str,
        status_code: int | None = None,
    ) -> None:
        self.errors[field_name].append(field_error)
        self.message = field_error
        self.is_error = True
        if status_code is not None:
            self.status_code = status_code

    def concat(self, other: ErrorCollector) -> None:
        for field_name, field_errors in other.errors.items():
            self.errors[field_name].extend(field_errors)
        if other.is_error:
            self.message = other.message
            self.status_code = other.status_code
            self.is_error = True

    def raise_if_errors(self) -> None:
        if not self.is_error:
            return
        raise ApiError(
            status_code=self.status_code,
            message=self.message,
            details=[
                {"field": field, "messages": messages}
                for field, messages in self.errors.items()
            ],
        )


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "details": exc.details},
        )

    @app.exception_handler(Exception)
    async def global_500_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": t("ERR_INTERNAL_SERVER_ERROR"), "details": []},
        )
