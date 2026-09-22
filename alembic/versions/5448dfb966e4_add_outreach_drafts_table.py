"""add outreach drafts table

Revision ID: 5448dfb966e4
Revises: 1e69cbaa7cc9
Create Date: 2026-09-21 16:32:37.697391

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5448dfb966e4'
down_revision: Union[str, Sequence[str], None] = '1e69cbaa7cc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the outreach drafts table."""
    op.create_table(
        "outreach_drafts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "follow_up_task_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "subject",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "model",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'approved', 'sent')",
            name="ck_outreach_drafts_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["follow_up_task_id"],
            ["follow_up_tasks.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_outreach_drafts_id"),
        "outreach_drafts",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_outreach_drafts_follow_up_task_id"),
        "outreach_drafts",
        ["follow_up_task_id"],
        unique=True,
    )


def downgrade() -> None:
    """Remove the outreach drafts table."""
    op.drop_index(
        op.f("ix_outreach_drafts_follow_up_task_id"),
        table_name="outreach_drafts",
    )
    op.drop_index(
        op.f("ix_outreach_drafts_id"),
        table_name="outreach_drafts",
    )
    op.drop_table("outreach_drafts")
