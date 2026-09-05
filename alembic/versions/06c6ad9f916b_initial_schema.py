"""initial schema

Revision ID: 06c6ad9f916b
Revises: 
Create Date: 2026-09-01 12:31:56.956665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06c6ad9f916b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial tickets table."""
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tickets_id"),
        "tickets",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the initial tickets table."""
    op.drop_index(
        op.f("ix_tickets_id"),
        table_name="tickets",
    )
    op.drop_table("tickets")
