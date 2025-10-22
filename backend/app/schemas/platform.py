from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.db.models.platform import Platform


class CategoryRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., ge=1)
    name: str


class TagRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., ge=1)
    name: str


class PlatformBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    url: Optional[str] = Field(default=None, max_length=500)
    category_ids: List[int] = Field(default_factory=list)
    tag_ids: List[int] = Field(default_factory=list)
    related_platform_ids: List[int] = Field(default_factory=list)
    links: Optional["PlatformLinks"] = None


class PlatformCreate(PlatformBase):
    pass


class PlatformUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    url: Optional[str] = Field(default=None, max_length=500)
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None
    related_platform_ids: Optional[List[int]] = None
    links: Optional["PlatformLinks"] = None


class PlatformLinks(BaseModel):
    ios: Optional[str] = Field(default=None, max_length=500)
    android: Optional[str] = Field(default=None, max_length=500)
    web: Optional[str] = Field(default=None, max_length=500)

    @field_validator("ios", "android", "web")
    @classmethod
    def empty_to_none(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            return None
        return value


class PlatformSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str


class PlatformRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: Optional[str]
    url: Optional[str]
    categories: List[CategoryRef]
    tags: List[TagRef]
    links: PlatformLinks = Field(default_factory=PlatformLinks)
    related_platforms: List[PlatformSummary] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def build_from_orm(cls, value):
        if isinstance(value, Platform):
            return {
                "id": value.id,
                "slug": value.slug,
                "name": value.name,
                "description": value.description,
                "url": value.url,
                "categories": value.categories,
                "tags": value.tags,
                "links": {
                    "ios": value.ios_url,
                    "android": value.android_url,
                    "web": value.web_url,
                },
                "related_platforms": value.all_related_platforms,
            }
        return value


PlatformBase.model_rebuild()
PlatformCreate.model_rebuild()
PlatformUpdate.model_rebuild()
PlatformRead.model_rebuild()
