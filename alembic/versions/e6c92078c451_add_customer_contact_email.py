"""add customer contact email

Revision ID: e6c92078c451
Revises: 957529aaeeee
Create Date: 2026-09-30 13:35:00.923504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6c92078c451'
down_revision: Union[str, Sequence[str], None] = '957529aaeeee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add an optional customer contact email."""
    op.add_column(
        "customers",
        sa.Column("contact_email", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    """Remove the customer contact email."""
    op.drop_column("customers", "contact_email")
