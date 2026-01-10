"""AtroZ Dashboard API error helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi.responses import JSONResponse

from .api_v1_schemas import APIError


@dataclass(frozen=True, slots=True)
class AtrozAPIException(Exception):
    status: int
    code: str
    message: str
    details: dict[str, Any] | None = None
    retry_after: int | None = None


def api_error_response(exc: AtrozAPIException) -> JSONResponse:
    payload = APIError(
        status=exc.status,
        code=exc.code,
        message=exc.message,
        details=exc.details,
        retryAfter=exc.retry_after,
    ).model_dump(mode="json")

    headers: dict[str, str] = {}
    if exc.retry_after is not None:
        headers["Retry-After"] = str(exc.retry_after)

    return JSONResponse(status_code=exc.status, content=payload, headers=headers)
