from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.slugs import slugify
from app.db.models import Collection


def generate_unique_slug(db: Session, title: str, current_id: Optional[int] = None) -> str:
    base_slug = slugify(title)
    candidate = base_slug
    index = 1

    while True:
        stmt = select(Collection.id).where(Collection.slug == candidate)
        if current_id is not None:
            stmt = stmt.where(Collection.id != current_id)
        exists = db.execute(stmt).scalar_one_or_none()
        if exists is None:
            return candidate
        index += 1
        candidate = f"{base_slug}-{index}"
