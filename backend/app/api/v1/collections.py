from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_current_admin, get_db
from app.db.models import Collection, CollectionPlatform, Platform
from app.schemas.collection import (
    CollectionCreate,
    CollectionMetrics,
    CollectionRead,
    CollectionUpdate,
)
from app.schemas.common import ApiResponse
from app.services.analytics import fetch_collection_metrics
from app.services.collections import generate_unique_slug

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("/", response_model=ApiResponse[List[CollectionRead]])
def list_collections(
    only_public: bool = Query(default=True, description="공개된 컬렉션만 조회"),
    featured: Optional[bool] = Query(default=None, description="추천 컬렉션 필터"),
    limit: Optional[int] = Query(default=12, ge=1, le=50, description="가져올 개수"),
    db: Session = Depends(get_db),
) -> ApiResponse[List[CollectionRead]]:
    stmt = (
        select(Collection)
        .options(
            selectinload(Collection.platforms),
            selectinload(Collection.platform_links).joinedload(CollectionPlatform.platform),
        )
        .order_by(Collection.display_order.asc(), Collection.trending_score.desc())
    )
    if only_public:
        stmt = stmt.where(Collection.is_public.is_(True))
    if featured is not None:
        stmt = stmt.where(Collection.is_featured.is_(featured))
    if limit:
        stmt = stmt.limit(limit)

    collections = db.execute(stmt).scalars().unique().all()
    metrics_map = fetch_collection_metrics(db, [collection.id for collection in collections])
    for collection in collections:
        setattr(collection, "__metrics__", metrics_map.get(collection.id, CollectionMetrics()))
    return ApiResponse(data=collections)


@router.get("/{slug}", response_model=ApiResponse[CollectionRead])
def get_collection(slug: str, db: Session = Depends(get_db)) -> ApiResponse[CollectionRead]:
    collection = _get_collection_by_slug_or_404(db, slug)
    metrics_map = fetch_collection_metrics(db, [collection.id])
    setattr(collection, "__metrics__", metrics_map.get(collection.id, CollectionMetrics()))
    return ApiResponse(data=collection)


@router.post(
    "/",
    response_model=ApiResponse[CollectionRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
def create_collection(payload: CollectionCreate, db: Session = Depends(get_db)) -> ApiResponse[CollectionRead]:
    platform_links = _build_platform_links(db, payload.platform_ids)
    slug = generate_unique_slug(db, payload.title)
    collection = Collection(
        title=payload.title,
        slug=slug,
        description=payload.description,
        highlight=payload.highlight,
        cover_image_url=payload.cover_image_url,
        is_public=payload.is_public,
        is_featured=payload.is_featured,
        display_order=payload.display_order,
        published_at=payload.published_at,
        platform_links=platform_links,
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    setattr(collection, "__metrics__", CollectionMetrics())
    return ApiResponse(message="컬렉션이 생성되었습니다.", data=collection)


@router.put(
    "/{collection_id}",
    response_model=ApiResponse[CollectionRead],
    dependencies=[Depends(get_current_admin)],
)
def update_collection(
    collection_id: int,
    payload: CollectionUpdate,
    db: Session = Depends(get_db),
) -> ApiResponse[CollectionRead]:
    collection = _get_collection_or_404(db, collection_id)

    if payload.title is not None:
        if payload.title != collection.title:
            collection.slug = generate_unique_slug(db, payload.title, current_id=collection.id)
        collection.title = payload.title
    if payload.description is not None:
        collection.description = payload.description
    if payload.highlight is not None:
        collection.highlight = payload.highlight
    if payload.cover_image_url is not None:
        collection.cover_image_url = payload.cover_image_url
    if payload.is_public is not None:
        collection.is_public = payload.is_public
    if payload.is_featured is not None:
        collection.is_featured = payload.is_featured
    if payload.display_order is not None:
        collection.display_order = payload.display_order
    if "published_at" in payload.model_fields_set:
        collection.published_at = payload.published_at

    if payload.platform_ids is not None:
        collection.platform_links = _build_platform_links(db, payload.platform_ids)

    db.add(collection)
    db.commit()
    db.refresh(collection)
    metrics_map = fetch_collection_metrics(db, [collection.id])
    setattr(collection, "__metrics__", metrics_map.get(collection.id, CollectionMetrics()))
    return ApiResponse(message="컬렉션이 수정되었습니다.", data=collection)


@router.delete(
    "/{collection_id}",
    response_model=ApiResponse[CollectionRead],
    dependencies=[Depends(get_current_admin)],
)
def delete_collection(collection_id: int, db: Session = Depends(get_db)) -> ApiResponse[CollectionRead]:
    collection = _get_collection_or_404(db, collection_id)
    payload = CollectionRead.model_validate(collection)

    db.delete(collection)
    db.commit()
    return ApiResponse(message="컬렉션이 삭제되었습니다.", data=payload)


def _get_collection_or_404(db: Session, collection_id: int) -> Collection:
    collection = db.execute(
        select(Collection)
        .options(
            selectinload(Collection.platforms),
            selectinload(Collection.platform_links).joinedload(CollectionPlatform.platform),
        )
        .where(Collection.id == collection_id)
    ).scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="컬렉션을 찾을 수 없습니다.")
    return collection


def _get_collection_by_slug_or_404(db: Session, slug: str) -> Collection:
    collection = db.execute(
        select(Collection)
        .options(
            selectinload(Collection.platforms),
            selectinload(Collection.platform_links).joinedload(CollectionPlatform.platform),
        )
        .where(Collection.slug == slug)
    ).scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="컬렉션을 찾을 수 없습니다.")
    return collection


def _build_platform_links(db: Session, platform_ids: List[int]) -> List[CollectionPlatform]:
    if not platform_ids:
        return []

    deduped: List[int] = []
    seen = set()
    for platform_id in platform_ids:
        if platform_id not in seen:
            seen.add(platform_id)
            deduped.append(platform_id)

    existing_ids = set(
        db.execute(select(Platform.id).where(Platform.id.in_(deduped))).scalars().all()
    )
    if len(existing_ids) != len(deduped):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효하지 않은 플랫폼 ID가 포함되어 있습니다.")

    return [CollectionPlatform(platform_id=platform_id, position=index) for index, platform_id in enumerate(deduped)]
