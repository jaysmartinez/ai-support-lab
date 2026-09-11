"""add follow up tasks table

Revision ID: 1e69cbaa7cc9
Revises: 461232fafbb9
Create Date: 2026-09-11 17:10:20.114960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e69cbaa7cc9'
down_revision: Union[str, Sequence[str], None] = '461232fafbb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the follow-up tasks table."""
    op.create_table(
        "follow_up_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("task_type", sa.String(length=100), nullable=False),
        sa.Column("recommended_action", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
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
            "status IN ('open', 'completed', 'cancelled')",
            name="ck_follow_up_tasks_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_follow_up_tasks_id"),
        "follow_up_tasks",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_follow_up_tasks_customer_id"),
        "follow_up_tasks",
        ["customer_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the follow-up tasks table."""
    op.drop_index(
        op.f("ix_follow_up_tasks_customer_id"),
        table_name="follow_up_tasks",
    )
    op.drop_index(
        op.f("ix_follow_up_tasks_id"),
        table_name="follow_up_tasks",
    )
    op.drop_table("follow_up_tasks")