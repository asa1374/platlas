from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import get_settings
from app.middleware.error_handling import ExceptionHandlingMiddleware
from app.schemas.common import ApiResponse

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.add_middleware(ExceptionHandlingMiddleware)


@app.get("/health", response_model=ApiResponse[str])
def healthcheck() -> ApiResponse[str]:
    return ApiResponse(message="ok", data="healthy")


app.include_router(api_router, prefix=f"{settings.api_prefix}/v1")
