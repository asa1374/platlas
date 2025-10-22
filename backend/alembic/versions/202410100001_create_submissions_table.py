"""create submissions table

Revision ID: 202410100001
Revises: 202410070001_add_platform_links_and_relations
Create Date: 2024-10-10 00:01:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202410100001"
down_revision: Union[str, None] = "202410070001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    submission_status = sa.Enum("pending", "approved", "rejected", name="submission_status")
    submission_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("submitter_name", sa.String(length=255), nullable=False),
        sa.Column("submitter_email", sa.String(length=255), nullable=False),
        sa.Column("platform_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        sa.Column("ios_url", sa.String(length=500), nullable=True),
        sa.Column("android_url", sa.String(length=500), nullable=True),
        sa.Column("web_url", sa.String(length=500), nullable=True),
        sa.Column("screenshot_url", sa.String(length=1024), nullable=True),
        sa.Column(
            "status",
            submission_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("platform_id", sa.Integer(), sa.ForeignKey("platforms.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
        ),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_submissions_platform_name",
        "submissions",
        ["platform_name"],
    )


def downgrade() -> None:
    op.drop_index("ix_submissions_platform_name", table_name="submissions")
    op.drop_table("submissions")
    submission_status = sa.Enum(name="submission_status")
    submission_status.drop(op.get_bind(), checkfirst=True)
