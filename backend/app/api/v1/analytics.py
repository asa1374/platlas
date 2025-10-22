from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_admin
from app.schemas.analytics import AnalyticsDashboard, AnalyticsEvent
from app.schemas.common import ApiResponse
from app.services.analytics import analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/events", response_model=ApiResponse[None], status_code=status.HTTP_202_ACCEPTED)
async def log_event(payload: AnalyticsEvent) -> ApiResponse[None]:
    await analytics.enqueue_event(payload.model_dump())
    return ApiResponse(message="이벤트가 큐에 저장되었습니다.")


@router.get(
    "/dashboard",
    response_model=ApiResponse[AnalyticsDashboard],
    dependencies=[Depends(get_current_admin)],
)
async def get_dashboard(days: int = 14, top_limit: int = 5) -> ApiResponse[AnalyticsDashboard]:
    dashboard = await analytics.get_dashboard(days=days, top_limit=top_limit)
    return ApiResponse(data=dashboard)
