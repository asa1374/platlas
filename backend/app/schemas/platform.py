from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


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


class PlatformCreate(PlatformBase):
    pass


class PlatformUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    url: Optional[str] = Field(default=None, max_length=500)
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None


class PlatformRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    url: Optional[str]
    categories: List[CategoryRef]
    tags: List[TagRef]
