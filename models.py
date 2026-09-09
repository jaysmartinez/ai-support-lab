from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from database import Base
from sqlalchemy.orm import relationship

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    category = Column(String(100), nullable=True)
    notes = relationship(
        "TicketNote",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )

class TicketNote(Base):
    __tablename__ = "ticket_notes"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id"),
        nullable=False,
    )

    content = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    ticket = relationship(
        "Ticket",
        back_populates="notes",
    )

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    industry = Column(String(100), nullable=False)
    account_owner = Column(String(255), nullable=False)

    payment_volume = Column(Numeric(14, 2), nullable=False)
    payment_volume_change_30d = Column(Float, nullable=False)

    product_usage = Column(Integer, nullable=False)
    product_usage_change_30d = Column(Float, nullable=False)

    open_support_tickets = Column(Integer, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=False)

    features_adopted = Column(Integer, nullable=False)
    total_available_features = Column(Integer, nullable=False)

    renewal_date = Column(Date, nullable=False)

    health_score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "payment_volume >= 0",
            name="ck_customers_payment_volume_nonnegative",
        ),
        CheckConstraint(
            "product_usage >= 0",
            name="ck_customers_product_usage_nonnegative",
        ),
        CheckConstraint(
            "open_support_tickets >= 0",
            name="ck_customers_open_tickets_nonnegative",
        ),
        CheckConstraint(
            "features_adopted >= 0",
            name="ck_customers_features_adopted_nonnegative",
        ),
        CheckConstraint(
            "total_available_features > 0",
            name="ck_customers_total_features_positive",
        ),
        CheckConstraint(
            "features_adopted <= total_available_features",
            name="ck_customers_feature_counts_valid",
        ),
        CheckConstraint(
            "health_score BETWEEN 0 AND 100",
            name="ck_customers_health_score_range",
        ),
        CheckConstraint(
            "risk_level IN ('high', 'medium', 'healthy')",
            name="ck_customers_risk_level_valid",
        ),
    )