from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.platform import PlatformSummary


class CollectionPlatformSummary(PlatformSummary):
    pass


class CollectionMetrics(BaseModel):
    views: int = 0
    clicks: int = 0
    trending_score: float = 0.0


class CollectionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    highlight: Optional[str] = Field(default=None, max_length=255)
    cover_image_url: Optional[str] = Field(default=None, max_length=500)
    is_public: bool = False
    is_featured: bool = False
    display_order: int = Field(default=0, ge=0)
    platform_ids: List[int] = Field(default_factory=list)


class CollectionCreate(CollectionBase):
    published_at: Optional[datetime] = None


class CollectionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    highlight: Optional[str] = Field(default=None, max_length=255)
    cover_image_url: Optional[str] = Field(default=None, max_length=500)
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = Field(default=None, ge=0)
    platform_ids: Optional[List[int]] = None
    published_at: Optional[datetime] = None


class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: Optional[str]
    highlight: Optional[str]
    cover_image_url: Optional[str]
    is_public: bool
    is_featured: bool
    display_order: int
    trending_score: float
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    platforms: List[CollectionPlatformSummary] = Field(default_factory=list)
    metrics: CollectionMetrics = Field(default_factory=CollectionMetrics)

    @model_validator(mode="before")
    @classmethod
    def build_from_orm(cls, value):
        if isinstance(value, dict):
            return value

        collection = value
        payload = {
            "id": collection.id,
            "slug": collection.slug,
            "title": collection.title,
            "description": collection.description,
            "highlight": collection.highlight,
            "cover_image_url": collection.cover_image_url,
            "is_public": collection.is_public,
            "is_featured": collection.is_featured,
            "display_order": collection.display_order,
            "trending_score": collection.trending_score,
            "published_at": collection.published_at,
            "created_at": collection.created_at,
            "updated_at": collection.updated_at,
            "platforms": [CollectionPlatformSummary.model_validate(p) for p in getattr(collection, "platforms", [])],
        }

        metrics = getattr(collection, "__metrics__", None)
        if metrics:
            payload["metrics"] = metrics
        return payload


class CollectionListResponse(BaseModel):
    items: List[CollectionRead]
    total: int


CollectionCreate.model_rebuild()
CollectionUpdate.model_rebuild()
CollectionRead.model_rebuild()
CollectionListResponse.model_rebuild()
