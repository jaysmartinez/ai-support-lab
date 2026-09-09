"""add customers table

Revision ID: 461232fafbb9
Revises: 696115f05b4c
Create Date: 2026-09-09 18:26:51.646940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '461232fafbb9'
down_revision: Union[str, Sequence[str], None] = '696115f05b4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the customers table."""
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("industry", sa.String(length=100), nullable=False),
        sa.Column("account_owner", sa.String(length=255), nullable=False),
        sa.Column("payment_volume", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("payment_volume_change_30d", sa.Float(), nullable=False),
        sa.Column("product_usage", sa.Integer(), nullable=False),
        sa.Column("product_usage_change_30d", sa.Float(), nullable=False),
        sa.Column("open_support_tickets", sa.Integer(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("features_adopted", sa.Integer(), nullable=False),
        sa.Column("total_available_features", sa.Integer(), nullable=False),
        sa.Column("renewal_date", sa.Date(), nullable=False),
        sa.Column("health_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "payment_volume >= 0",
            name="ck_customers_payment_volume_nonnegative",
        ),
        sa.CheckConstraint(
            "product_usage >= 0",
            name="ck_customers_product_usage_nonnegative",
        ),
        sa.CheckConstraint(
            "open_support_tickets >= 0",
            name="ck_customers_open_tickets_nonnegative",
        ),
        sa.CheckConstraint(
            "features_adopted >= 0",
            name="ck_customers_features_adopted_nonnegative",
        ),
        sa.CheckConstraint(
            "total_available_features > 0",
            name="ck_customers_total_features_positive",
        ),
        sa.CheckConstraint(
            "features_adopted <= total_available_features",
            name="ck_customers_feature_counts_valid",
        ),
        sa.CheckConstraint(
            "health_score BETWEEN 0 AND 100",
            name="ck_customers_health_score_range",
        ),
        sa.CheckConstraint(
            "risk_level IN ('high', 'medium', 'healthy')",
            name="ck_customers_risk_level_valid",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_customers_id"),
        "customers",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_customers_name"),
        "customers",
        ["name"],
        unique=True,
    )


def downgrade() -> None:
    """Remove the customers table."""
    op.drop_index(
        op.f("ix_customers_name"),
        table_name="customers",
    )
    op.drop_index(
        op.f("ix_customers_id"),
        table_name="customers",
    )
    op.drop_table("customers")
