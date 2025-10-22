"""add slug, links, and relations to platforms

Revision ID: 202410070001
Revises: 202403040001
Create Date: 2024-10-07 00:01:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.core.slugs import slugify

# revision identifiers, used by Alembic.
revision: str = "202410070001"
down_revision: Union[str, None] = "202403040001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("platforms", sa.Column("slug", sa.String(length=255), nullable=True))
    op.add_column("platforms", sa.Column("ios_url", sa.String(length=500), nullable=True))
    op.add_column("platforms", sa.Column("android_url", sa.String(length=500), nullable=True))
    op.add_column("platforms", sa.Column("web_url", sa.String(length=500), nullable=True))

    bind = op.get_bind()
    platforms = bind.execute(sa.text("SELECT id, name FROM platforms")).fetchall()
    existing_slugs: set[str] = set()
    for platform in platforms:
        base_slug = slugify(platform.name)
        slug_candidate = base_slug
        index = 1
        while slug_candidate in existing_slugs:
            index += 1
            slug_candidate = f"{base_slug}-{index}"
        existing_slugs.add(slug_candidate)
        bind.execute(
            sa.text("UPDATE platforms SET slug = :slug WHERE id = :id"),
            {"slug": slug_candidate, "id": platform.id},
        )

    op.alter_column("platforms", "slug", nullable=False)
    op.create_index("ix_platforms_slug", "platforms", ["slug"], unique=True)

    op.create_table(
        "platform_related_platforms",
        sa.Column("platform_id", sa.Integer(), nullable=False),
        sa.Column("related_platform_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["platform_id"], ["platforms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["related_platform_id"], ["platforms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("platform_id", "related_platform_id"),
    )


def downgrade() -> None:
    op.drop_table("platform_related_platforms")
    op.drop_index("ix_platforms_slug", table_name="platforms")
    op.drop_column("platforms", "web_url")
    op.drop_column("platforms", "android_url")
    op.drop_column("platforms", "ios_url")
    op.drop_column("platforms", "slug")
