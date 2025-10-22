from fastapi import APIRouter

from app.api.v1 import admin, platforms, submissions

api_router = APIRouter()
api_router.include_router(platforms.router)
api_router.include_router(submissions.router)
api_router.include_router(admin.router)

__all__ = ["api_router"]
