from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_db
from app.db.models import Category, Platform, Tag, platform_categories, platform_tags
from app.schemas.common import ApiResponse
from app.schemas.platform import (
    CategoryRef,
    PlatformCreate,
    PlatformLinks,
    PlatformRead,
    PlatformSummary,
    PlatformUpdate,
    TagRef,
)
from app.services.platforms import generate_unique_slug

router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.get("/", response_model=ApiResponse[List[PlatformRead]])
def list_platforms(
    search: Optional[str] = Query(default=None, description="Search platforms by name or description"),
    category_ids: List[int] = Query(default_factory=list, description="Filter by category ids"),
    tag_ids: List[int] = Query(default_factory=list, description="Filter by tag ids"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ApiResponse[List[PlatformRead]]:
    base_query: Select[int] = select(Platform.id).select_from(Platform)

    if search:
        term = f"%{search.strip()}%"
        base_query = base_query.where(
            or_(Platform.name.ilike(term), Platform.description.ilike(term))
        )

    if category_ids:
        unique_category_ids = set(category_ids)
        category_subquery = (
            select(platform_categories.c.platform_id)
            .where(platform_categories.c.category_id.in_(unique_category_ids))
            .group_by(platform_categories.c.platform_id)
            .having(func.count(func.distinct(platform_categories.c.category_id)) == len(unique_category_ids))
        )
        base_query = base_query.where(Platform.id.in_(category_subquery))

    if tag_ids:
        unique_tag_ids = set(tag_ids)
        tag_subquery = (
            select(platform_tags.c.platform_id)
            .where(platform_tags.c.tag_id.in_(unique_tag_ids))
            .group_by(platform_tags.c.platform_id)
            .having(func.count(func.distinct(platform_tags.c.tag_id)) == len(unique_tag_ids))
        )
        base_query = base_query.where(Platform.id.in_(tag_subquery))

    filtered_query = base_query.distinct()
    subquery = filtered_query.subquery()
    total = db.execute(select(func.count()).select_from(subquery)).scalar_one()

    offset = (page - 1) * page_size
    paginated_ids = db.execute(
        filtered_query.order_by(Platform.name.asc()).offset(offset).limit(page_size)
    ).scalars().all()

    if not paginated_ids:
        meta = _build_meta(db, total=total, page=page, page_size=page_size)
        return ApiResponse(data=[], meta=meta)

    platforms_query = (
        select(Platform)
        .options(
            selectinload(Platform.categories),
            selectinload(Platform.tags),
            selectinload(Platform.related_platforms),
            selectinload(Platform.related_to),
        )
        .where(Platform.id.in_(paginated_ids))
        .order_by(Platform.name.asc())
    )
    platforms = db.execute(platforms_query).scalars().unique().all()
    meta = _build_meta(db, total=total, page=page, page_size=page_size)
    return ApiResponse(data=platforms, meta=meta)


@router.get("/{slug}", response_model=ApiResponse[PlatformRead])
def get_platform(slug: str, db: Session = Depends(get_db)) -> ApiResponse[PlatformRead]:
    platform = _get_platform_by_slug_or_404(db, slug)
    return ApiResponse(data=platform)


@router.post("/", response_model=ApiResponse[PlatformRead], status_code=status.HTTP_201_CREATED)
def create_platform(payload: PlatformCreate, db: Session = Depends(get_db)) -> ApiResponse[PlatformRead]:
    categories = _load_categories(db, payload.category_ids)
    tags = _load_tags(db, payload.tag_ids)
    related_platforms = _load_related_platforms(db, payload.related_platform_ids)
    slug = generate_unique_slug(db, payload.name)

    links = payload.links or PlatformLinks()

    platform = Platform(
        name=payload.name,
        slug=slug,
        description=payload.description,
        url=payload.url,
        ios_url=links.ios,
        android_url=links.android,
        web_url=links.web,
        categories=categories,
        tags=tags,
        related_platforms=related_platforms,
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
        if payload.name != platform.name:
            platform.slug = generate_unique_slug(db, payload.name, current_id=platform.id)
        platform.name = payload.name
    if payload.description is not None:
        platform.description = payload.description
    if payload.url is not None:
        platform.url = payload.url

    if payload.links is not None:
        links = payload.links
        platform.ios_url = links.ios
        platform.android_url = links.android
        platform.web_url = links.web

    if payload.category_ids is not None:
        platform.categories = _load_categories(db, payload.category_ids)
    if payload.tag_ids is not None:
        platform.tags = _load_tags(db, payload.tag_ids)
    if payload.related_platform_ids is not None:
        platform.related_platforms = _load_related_platforms(
            db, payload.related_platform_ids, current_platform_id=platform.id
        )

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


def _build_meta(db: Session, *, total: int, page: int, page_size: int) -> dict:
    total_pages = (total + page_size - 1) // page_size if total else 0
    categories = db.execute(select(Category).order_by(Category.name.asc())).scalars().all()
    tags = db.execute(select(Tag).order_by(Tag.name.asc())).scalars().all()

    return {
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": total_pages,
        },
        "filters": {
            "categories": [CategoryRef.model_validate(cat).model_dump() for cat in categories],
            "tags": [TagRef.model_validate(tag).model_dump() for tag in tags],
        },
    }


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


def _load_related_platforms(
    db: Session, related_ids: List[int], current_platform_id: Optional[int] = None
) -> List[Platform]:
    if not related_ids:
        return []

    unique_ids = {platform_id for platform_id in related_ids if platform_id != current_platform_id}
    if not unique_ids:
        return []

    platforms = db.execute(select(Platform).where(Platform.id.in_(unique_ids))).scalars().all()
    if len(platforms) != len(unique_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid related platform IDs",
        )
    return platforms


def _get_platform_or_404(db: Session, platform_id: int) -> Platform:
    stmt = (
        select(Platform)
        .options(
            selectinload(Platform.categories),
            selectinload(Platform.tags),
            selectinload(Platform.related_platforms),
            selectinload(Platform.related_to),
        )
        .where(Platform.id == platform_id)
    )
    platform = db.execute(stmt).scalars().first()
    if platform is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Platform not found")
    return platform


def _get_platform_by_slug_or_404(db: Session, slug: str) -> Platform:
    stmt = (
        select(Platform)
        .options(
            selectinload(Platform.categories),
            selectinload(Platform.tags),
            selectinload(Platform.related_platforms),
            selectinload(Platform.related_to),
        )
        .where(Platform.slug == slug)
    )
    platform = db.execute(stmt).scalars().first()
    if platform is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Platform not found")
    return platform

