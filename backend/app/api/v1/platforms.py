from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_db
from app.db.models import Category, Platform, Tag
from app.schemas.common import ApiResponse
from app.schemas.platform import PlatformCreate, PlatformRead, PlatformUpdate

router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.get("/", response_model=ApiResponse[List[PlatformRead]])
def list_platforms(
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> ApiResponse[List[PlatformRead]]:
    query = select(Platform).options(
        selectinload(Platform.categories),
        selectinload(Platform.tags),
    ).distinct()

    if category_id is not None:
        query = query.join(Platform.categories).where(Category.id == category_id)

    if tag_id is not None:
        query = query.join(Platform.tags).where(Tag.id == tag_id)

    platforms = db.execute(query).scalars().unique().all()
    return ApiResponse(data=platforms)


@router.get("/{platform_id}", response_model=ApiResponse[PlatformRead])
def get_platform(platform_id: int, db: Session = Depends(get_db)) -> ApiResponse[PlatformRead]:
    platform = _get_platform_or_404(db, platform_id)
    return ApiResponse(data=platform)


@router.post("/", response_model=ApiResponse[PlatformRead], status_code=status.HTTP_201_CREATED)
def create_platform(payload: PlatformCreate, db: Session = Depends(get_db)) -> ApiResponse[PlatformRead]:
    categories = _load_categories(db, payload.category_ids)
    tags = _load_tags(db, payload.tag_ids)

    platform = Platform(
        name=payload.name,
        description=payload.description,
        url=payload.url,
        categories=categories,
        tags=tags,
    )
    db.add(platform)
    db.commit()
    db.refresh(platform)
    return ApiResponse(message="Platform created", data=platform)


@router.put("/{platform_id}", response_model=ApiResponse[PlatformRead])
def update_platform(
    platform_id: int,
    payload: PlatformUpdate,
    db: Session = Depends(get_db),
) -> ApiResponse[PlatformRead]:
    platform = _get_platform_or_404(db, platform_id)

    if payload.name is not None:
        platform.name = payload.name
    if payload.description is not None:
        platform.description = payload.description
    if payload.url is not None:
        platform.url = payload.url

    if payload.category_ids is not None:
        platform.categories = _load_categories(db, payload.category_ids)
    if payload.tag_ids is not None:
        platform.tags = _load_tags(db, payload.tag_ids)

    db.add(platform)
    db.commit()
    db.refresh(platform)
    return ApiResponse(message="Platform updated", data=platform)


@router.delete("/{platform_id}", response_model=ApiResponse[PlatformRead])
def delete_platform(platform_id: int, db: Session = Depends(get_db)) -> ApiResponse[PlatformRead]:
    platform = _get_platform_or_404(db, platform_id)
    payload = PlatformRead.model_validate(platform)

    db.delete(platform)
    db.commit()
    return ApiResponse(message="Platform deleted", data=payload)


def _load_categories(db: Session, category_ids: List[int]) -> List[Category]:
    if not category_ids:
        return []

    unique_ids = set(category_ids)
    categories = db.execute(select(Category).where(Category.id.in_(unique_ids))).scalars().all()
    if len(categories) != len(unique_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category IDs")
    return categories


def _load_tags(db: Session, tag_ids: List[int]) -> List[Tag]:
    if not tag_ids:
        return []

    unique_ids = set(tag_ids)
    tags = db.execute(select(Tag).where(Tag.id.in_(unique_ids))).scalars().all()
    if len(tags) != len(unique_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tag IDs")
    return tags


def _get_platform_or_404(db: Session, platform_id: int) -> Platform:
    stmt = (
        select(Platform)
        .options(selectinload(Platform.categories), selectinload(Platform.tags))
        .where(Platform.id == platform_id)
    )
    platform = db.execute(stmt).scalars().first()
    if platform is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Platform not found")
    return platform
