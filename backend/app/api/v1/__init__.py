from fastapi import APIRouter

from app.api.v1 import platforms

api_router = APIRouter()
api_router.include_router(platforms.router)

__all__ = ["api_router"]
