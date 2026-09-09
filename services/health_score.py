from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    HEALTHY = "healthy"


@dataclass(frozen=True)
class HealthMetrics:
    payment_volume_change_30d: float
    product_usage_change_30d: float
    open_support_tickets: int
    last_login_at: datetime
    features_adopted: int
    total_available_features: int


@dataclass(frozen=True)
class HealthAssessment:
    score: int
    risk_level: RiskLevel
    factors: tuple[str, ...]


def calculate_health_score(
    metrics: HealthMetrics,
    *,
    as_of: date | None = None,
) -> HealthAssessment:
    """Calculate customer health using deterministic business rules."""
    if metrics.open_support_tickets < 0:
        raise ValueError("open_support_tickets cannot be negative")

    if metrics.features_adopted < 0:
        raise ValueError("features_adopted cannot be negative")

    if metrics.total_available_features <= 0:
        raise ValueError("total_available_features must be greater than zero")

    if metrics.features_adopted > metrics.total_available_features:
        raise ValueError(
            "features_adopted cannot exceed total_available_features"
        )

    score = 70
    factors: list[str] = []

    if metrics.payment_volume_change_30d <= -30:
        score -= 25
        factors.append("Payment volume declined by at least 30%.")
    elif metrics.payment_volume_change_30d <= -15:
        score -= 15
        factors.append("Payment volume declined by at least 15%.")
    elif metrics.payment_volume_change_30d < 0:
        score -= 5
        factors.append("Payment volume declined slightly.")
    elif metrics.payment_volume_change_30d >= 20:
        score += 15
        factors.append("Payment volume grew by at least 20%.")
    elif metrics.payment_volume_change_30d >= 5:
        score += 8
        factors.append("Payment volume is growing.")

    if metrics.product_usage_change_30d <= -30:
        score -= 20
        factors.append("Product usage declined by at least 30%.")
    elif metrics.product_usage_change_30d <= -15:
        score -= 12
        factors.append("Product usage declined by at least 15%.")
    elif metrics.product_usage_change_30d < 0:
        score -= 5
        factors.append("Product usage declined slightly.")
    elif metrics.product_usage_change_30d >= 20:
        score += 10
        factors.append("Product usage grew by at least 20%.")
    elif metrics.product_usage_change_30d >= 5:
        score += 5
        factors.append("Product usage is growing.")

    if metrics.open_support_tickets >= 5:
        score -= 20
        factors.append("Five or more support tickets remain open.")
    elif metrics.open_support_tickets >= 3:
        score -= 12
        factors.append("Several support tickets remain open.")
    elif metrics.open_support_tickets >= 1:
        score -= 4
        factors.append("At least one support ticket remains open.")

    today = as_of or date.today()
    days_since_last_login = max(
        0,
        (today - metrics.last_login_at.date()).days,
    )

    if days_since_last_login >= 60:
        score -= 20
        factors.append("The customer has not logged in for at least 60 days.")
    elif days_since_last_login >= 30:
        score -= 12
        factors.append("The customer has not logged in for at least 30 days.")
    elif days_since_last_login >= 14:
        score -= 5
        factors.append("The customer has not logged in for at least 14 days.")

    adoption_rate = (
        metrics.features_adopted / metrics.total_available_features
    )

    if adoption_rate >= 0.80:
        score += 15
        factors.append("Feature adoption is at least 80%.")
    elif adoption_rate >= 0.60:
        score += 8
        factors.append("Feature adoption is at least 60%.")
    elif adoption_rate < 0.30:
        score -= 15
        factors.append("Feature adoption is below 30%.")
    elif adoption_rate < 0.50:
        score -= 8
        factors.append("Feature adoption is below 50%.")

    score = max(0, min(100, score))

    if score <= 49:
        risk_level = RiskLevel.HIGH
    elif score <= 74:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.HEALTHY

    return HealthAssessment(
        score=score,
        risk_level=risk_level,
        factors=tuple(factors),
    )