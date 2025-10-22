from __future__ import annotations

import logging
from typing import Awaitable, Callable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.schemas.common import ErrorResponse

logger = logging.getLogger(__name__)


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:  # type: ignore[override]
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            logger.warning("Handled HTTPException: %s", exc.detail)
            payload = ErrorResponse(message=str(exc.detail))
            return JSONResponse(status_code=exc.status_code, content=payload.model_dump())
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unhandled exception: %s", exc)
            payload = ErrorResponse(message="Internal server error")
            return JSONResponse(status_code=500, content=payload.model_dump())
