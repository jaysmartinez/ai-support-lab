"""add outreach draft approval time

Revision ID: 957529aaeeee
Revises: 5448dfb966e4
Create Date: 2026-09-22 16:54:58.896247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '957529aaeeee'
down_revision: Union[str, Sequence[str], None] = '5448dfb966e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add and backfill the approval timestamp."""
    op.add_column(
        "outreach_drafts",
        sa.Column(
            "approved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE outreach_drafts
        SET approved_at = updated_at
        WHERE status = 'approved'
        """
    )


def downgrade() -> None:
    """Remove the approval timestamp."""
    op.drop_column("outreach_drafts", "approved_at")
