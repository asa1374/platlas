from __future__ import annotations

from typing import Dict, List

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


platform_categories = Table(
    "platform_categories",
    Base.metadata,
    Column("platform_id", ForeignKey("platforms.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)

platform_tags = Table(
    "platform_tags",
    Base.metadata,
    Column("platform_id", ForeignKey("platforms.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


platform_related_platforms = Table(
    "platform_related_platforms",
    Base.metadata,
    Column(
        "platform_id",
        ForeignKey("platforms.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "related_platform_id",
        ForeignKey("platforms.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    UniqueConstraint("platform_id", "related_platform_id", name="uq_platform_related"),
)


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ios_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    android_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    web_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    categories: Mapped[List["Category"]] = relationship(
        "Category",
        secondary=platform_categories,
        back_populates="platforms",
        lazy="selectin",
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=platform_tags,
        back_populates="platforms",
        lazy="selectin",
    )
    related_platforms: Mapped[List["Platform"]] = relationship(
        "Platform",
        secondary=platform_related_platforms,
        primaryjoin=id == platform_related_platforms.c.platform_id,
        secondaryjoin=id == platform_related_platforms.c.related_platform_id,
        backref="related_to",
        lazy="selectin",
    )

    @property
    def links(self) -> Dict[str, str | None]:
        return {
            "ios": self.ios_url,
            "android": self.android_url,
            "web": self.web_url,
        }

    @property
    def all_related_platforms(self) -> List["Platform"]:
        seen: Dict[int, Platform] = {}
        for item in self.related_platforms + list(getattr(self, "related_to", [])):
            if item.id not in seen:
                seen[item.id] = item
        return list(seen.values())


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    platforms: Mapped[List[Platform]] = relationship(
        "Platform",
        secondary=platform_categories,
        back_populates="categories",
        lazy="selectin",
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    platforms: Mapped[List[Platform]] = relationship(
        "Platform",
        secondary=platform_tags,
        back_populates="tags",
        lazy="selectin",
    )
