from datetime import date, datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from models import Customer, FollowUpTask
from services.risk_automation import (
    AUTOMATED_RISK_REVIEW_TASK_TYPE,
    build_automated_follow_up_action,
    run_risk_review,
)

def test_build_action_includes_customer_risk_factors():
    customer = Customer(
        name="Risky Account",
        payment_volume_change_30d=-18.5,
        product_usage_change_30d=-12,
        open_support_tickets=4,
        last_login_at=datetime(
            2026,
            8,
            20,
            tzinfo=timezone.utc,
        ),
        features_adopted=4,
        total_available_features=10,
        renewal_date=date(2026, 10, 15),
        health_score=32,
    )

    action = build_automated_follow_up_action(
        customer,
        as_of=date(2026, 9, 21),
    )

    assert action == (
        "Schedule a customer health review for Risky Account. "
        "Discuss: payment volume declined 18.5%, "
        "product usage declined 12.0%, "
        "4 support tickets are open, "
        "the customer has not logged in for 32 days, "
        "feature adoption is below 50%, "
        "renewal is in 24 days."
    )


def test_build_action_falls_back_to_health_score():
    customer = Customer(
        name="Low Score Account",
        payment_volume_change_30d=5,
        product_usage_change_30d=5,
        open_support_tickets=0,
        last_login_at=datetime(
            2026,
            9,
            20,
            tzinfo=timezone.utc,
        ),
        features_adopted=8,
        total_available_features=10,
        renewal_date=date(2027, 3, 1),
        health_score=45,
    )

    action = build_automated_follow_up_action(
        customer,
        as_of=date(2026, 9, 21),
    )

    assert action == (
        "Schedule a customer health review for Low Score Account. "
        "Discuss: the overall health score is 45."
    )


def test_run_risk_review_creates_task_without_duplicates():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine)

    Base.metadata.create_all(bind=engine)
    db = testing_session()

    timestamp = datetime(2026, 9, 21, tzinfo=timezone.utc)

    risky_customer = Customer(
        name="Automated Risk Test",
        industry="fintech",
        account_owner="Jay Martinez",
        payment_volume=25000,
        payment_volume_change_30d=-20,
        product_usage=80,
        product_usage_change_30d=-15,
        open_support_tickets=4,
        last_login_at=datetime(
            2026,
            8,
            20,
            tzinfo=timezone.utc,
        ),
        features_adopted=3,
        total_available_features=10,
        renewal_date=date(2026, 10, 15),
        health_score=35,
        risk_level="high",
        created_at=timestamp,
        updated_at=timestamp,
    )

    healthy_customer = Customer(
        name="Healthy Automation Test",
        industry="insurance",
        account_owner="Jay Martinez",
        payment_volume=100000,
        payment_volume_change_30d=10,
        product_usage=500,
        product_usage_change_30d=8,
        open_support_tickets=0,
        last_login_at=timestamp,
        features_adopted=9,
        total_available_features=10,
        renewal_date=date(2027, 3, 1),
        health_score=90,
        risk_level="healthy",
        created_at=timestamp,
        updated_at=timestamp,
    )

    db.add_all([risky_customer, healthy_customer])
    db.commit()

    first_result = run_risk_review(
        db,
        as_of=date(2026, 9, 21),
        now=timestamp,
    )

    assert first_result.customers_scanned == 2
    assert first_result.high_risk_customers == 1
    assert first_result.tasks_created == 1
    assert first_result.tasks_skipped == 0

    second_result = run_risk_review(
        db,
        as_of=date(2026, 9, 21),
        now=timestamp,
    )

    assert second_result.tasks_created == 0
    assert second_result.tasks_skipped == 1

    tasks = db.query(FollowUpTask).all()

    assert len(tasks) == 1
    assert tasks[0].customer_id == risky_customer.id
    assert (
        tasks[0].task_type
        == AUTOMATED_RISK_REVIEW_TASK_TYPE
    )
    assert tasks[0].status == "open"

    db.close()
    Base.metadata.drop_all(bind=engine)