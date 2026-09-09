from datetime import date, datetime, timezone

import pytest

from services.health_score import (
    HealthMetrics,
    RiskLevel,
    calculate_health_score,
)


def test_high_risk_customer():
    metrics = HealthMetrics(
        payment_volume_change_30d=-35,
        product_usage_change_30d=-40,
        open_support_tickets=6,
        last_login_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        features_adopted=2,
        total_available_features=10,
    )

    assessment = calculate_health_score(
        metrics,
        as_of=date(2026, 9, 9),
    )

    assert assessment.score == 0
    assert assessment.risk_level == RiskLevel.HIGH
    assert len(assessment.factors) == 5


def test_healthy_customer_score_is_capped_at_100():
    metrics = HealthMetrics(
        payment_volume_change_30d=25,
        product_usage_change_30d=25,
        open_support_tickets=0,
        last_login_at=datetime(2026, 9, 8, tzinfo=timezone.utc),
        features_adopted=9,
        total_available_features=10,
    )

    assessment = calculate_health_score(
        metrics,
        as_of=date(2026, 9, 9),
    )

    assert assessment.score == 100
    assert assessment.risk_level == RiskLevel.HEALTHY


def test_neutral_customer_is_medium_risk():
    metrics = HealthMetrics(
        payment_volume_change_30d=0,
        product_usage_change_30d=0,
        open_support_tickets=0,
        last_login_at=datetime(2026, 9, 8, tzinfo=timezone.utc),
        features_adopted=5,
        total_available_features=10,
    )

    assessment = calculate_health_score(
        metrics,
        as_of=date(2026, 9, 9),
    )

    assert assessment.score == 70
    assert assessment.risk_level == RiskLevel.MEDIUM
    assert assessment.factors == ()


def test_inactive_customer_receives_login_penalty():
    metrics = HealthMetrics(
        payment_volume_change_30d=0,
        product_usage_change_30d=0,
        open_support_tickets=0,
        last_login_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        features_adopted=5,
        total_available_features=10,
    )

    assessment = calculate_health_score(
        metrics,
        as_of=date(2026, 9, 9),
    )

    assert assessment.score == 58
    assert assessment.risk_level == RiskLevel.MEDIUM
    assert assessment.factors == (
        "The customer has not logged in for at least 30 days.",
    )


def test_features_adopted_cannot_exceed_total_features():
    metrics = HealthMetrics(
        payment_volume_change_30d=0,
        product_usage_change_30d=0,
        open_support_tickets=0,
        last_login_at=datetime(2026, 9, 8, tzinfo=timezone.utc),
        features_adopted=11,
        total_available_features=10,
    )

    with pytest.raises(
        ValueError,
        match="features_adopted cannot exceed total_available_features",
    ):
        calculate_health_score(
            metrics,
            as_of=date(2026, 9, 9),
        )