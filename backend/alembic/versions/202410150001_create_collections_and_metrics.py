"""create collections and metrics tables

Revision ID: 202410150001
Revises: 202410100001
Create Date: 2024-10-15 00:01:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202410150001"
down_revision: Union[str, None] = "202410100001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


COLLECTION_TABLE = "collections"
COLLECTION_PLATFORM_TABLE = "collection_platforms"
METRICS_DAILY_TABLE = "metrics_daily"


def upgrade() -> None:
    metric_entity_type = sa.Enum("collection", "platform", name="metric_entity_type")
    metric_entity_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        COLLECTION_TABLE,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("highlight", sa.String(length=255), nullable=True),
        sa.Column("cover_image_url", sa.String(length=500), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("trending_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_collections_slug"),
    )
    op.create_index("ix_collections_id", COLLECTION_TABLE, ["id"])
    op.create_index("ix_collections_slug", COLLECTION_TABLE, ["slug"], unique=True)

    op.create_table(
        COLLECTION_PLATFORM_TABLE,
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("platform_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.ForeignKeyConstraint(
            ["collection_id"], ["collections.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["platform_id"], ["platforms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("collection_id", "platform_id"),
        sa.UniqueConstraint("collection_id", "platform_id", name="uq_collection_platform"),
    )

    op.create_table(
        METRICS_DAILY_TABLE,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", metric_entity_type, nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("views", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
        ),
        sa.UniqueConstraint("entity_type", "entity_id", "date", name="uq_metric_daily_entity_date"),
    )
    op.create_index(
        "ix_metrics_daily_entity",
        METRICS_DAILY_TABLE,
        ["entity_type", "entity_id", "date"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_metrics_daily_entity", table_name=METRICS_DAILY_TABLE)
    op.drop_table(METRICS_DAILY_TABLE)

    op.drop_table(COLLECTION_PLATFORM_TABLE)

    op.drop_index("ix_collections_slug", table_name=COLLECTION_TABLE)
    op.drop_index("ix_collections_id", table_name=COLLECTION_TABLE)
    op.drop_table(COLLECTION_TABLE)

    metric_entity_type = sa.Enum(name="metric_entity_type")
    metric_entity_type.drop(op.get_bind(), checkfirst=True)
