from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.slugs import slugify
from app.db.models import Platform


def generate_unique_slug(db: Session, name: str, current_id: Optional[int] = None) -> str:
    base_slug = slugify(name)
    slug_candidate = base_slug
    index = 1

    while True:
        stmt = select(Platform.id).where(Platform.slug == slug_candidate)
        if current_id is not None:
            stmt = stmt.where(Platform.id != current_id)
        exists = db.execute(stmt).scalar_one_or_none()
        if exists is None:
            return slug_candidate
        index += 1
        slug_candidate = f"{base_slug}-{index}"
