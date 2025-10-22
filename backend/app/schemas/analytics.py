from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class AnalyticsEvent(BaseModel):
    entity_type: Literal["collection", "platform"]
    entity_id: int = Field(..., ge=1)
    event_type: Literal["view", "click"]
    occurred_at: Optional[datetime] = None
    metadata: Dict[str, str] | None = None

    @field_validator("metadata")
    @classmethod
    def normalize_metadata(cls, value: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if value is None:
            return None
        return {str(key): str(val) for key, val in value.items()}


class DailyMetricPoint(BaseModel):
    date: date
    views: int
    clicks: int


class TopCollectionMetric(BaseModel):
    collection_id: int
    slug: str
    title: str
    views: int
    clicks: int
    trending_score: float


class AnalyticsDashboard(BaseModel):
    daily: List[DailyMetricPoint]
    top_collections: List[TopCollectionMetric]
