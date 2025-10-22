from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List

from sqlalchemy import Boolean, Date, DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlight: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    trending_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    platform_links: Mapped[List["CollectionPlatform"]] = relationship(
        "CollectionPlatform",
        order_by="CollectionPlatform.position.asc()",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    platforms: Mapped[List["Platform"]] = relationship(
        "Platform",
        secondary="collection_platforms",
        order_by="CollectionPlatform.position.asc()",
        viewonly=True,
        lazy="selectin",
    )


class CollectionPlatform(Base):
    __tablename__ = "collection_platforms"
    __table_args__ = (
        UniqueConstraint("collection_id", "platform_id", name="uq_collection_platform"),
    )

    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True
    )
    platform_id: Mapped[int] = mapped_column(
        ForeignKey("platforms.id", ondelete="CASCADE"), primary_key=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    collection: Mapped[Collection] = relationship("Collection", back_populates="platform_links")
    platform: Mapped["Platform"] = relationship("Platform")


class MetricEntityType(str, Enum):
    COLLECTION = "collection"
    PLATFORM = "platform"


class MetricsDaily(Base):
    __tablename__ = "metrics_daily"
    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", "date", name="uq_metric_daily_entity_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_type: Mapped[MetricEntityType] = mapped_column(
        SqlEnum(MetricEntityType, name="metric_entity_type"), nullable=False
    )
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
