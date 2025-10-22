from __future__ import annotations

from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
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


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)

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
