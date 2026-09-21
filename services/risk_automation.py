from dataclasses import dataclass
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from models import Customer, FollowUpTask


AUTOMATED_RISK_REVIEW_TASK_TYPE = "automated_risk_review"

@dataclass
class RiskReviewResult:
    customers_scanned: int
    high_risk_customers: int
    tasks_created: int
    tasks_skipped: int

def build_automated_follow_up_action(
    customer: Customer,
    *,
    as_of: date | None = None,
) -> str:
    """Build a deterministic follow-up action from customer risk signals."""
    today = as_of or date.today()
    risk_factors: list[str] = []

    if customer.payment_volume_change_30d < 0:
        risk_factors.append(
            f"payment volume declined "
            f"{abs(customer.payment_volume_change_30d):.1f}%"
        )

    if customer.product_usage_change_30d < 0:
        risk_factors.append(
            f"product usage declined "
            f"{abs(customer.product_usage_change_30d):.1f}%"
        )

    if customer.open_support_tickets >= 3:
        risk_factors.append(
            f"{customer.open_support_tickets} support tickets are open"
        )

    days_since_login = max(
        0,
        (today - customer.last_login_at.date()).days,
    )

    if days_since_login >= 14:
        risk_factors.append(
            f"the customer has not logged in for {days_since_login} days"
        )

    adoption_rate = (
        customer.features_adopted
        / customer.total_available_features
    )

    if adoption_rate < 0.50:
        risk_factors.append("feature adoption is below 50%")

    days_until_renewal = (customer.renewal_date - today).days

    if 0 <= days_until_renewal <= 60:
        risk_factors.append(
            f"renewal is in {days_until_renewal} days"
        )

    if not risk_factors:
        risk_factors.append(
            f"the overall health score is {customer.health_score}"
        )

    return (
        f"Schedule a customer health review for {customer.name}. "
        f"Discuss: {', '.join(risk_factors)}."
    )

def run_risk_review(
    db: Session,
    *,
    as_of: date | None = None,
    now: datetime | None = None,
) -> RiskReviewResult:
    """Create missing follow-up tasks for high-risk customers."""
    review_date = as_of or date.today()
    timestamp = now or datetime.now(timezone.utc)

    customers_scanned = db.query(Customer).count()

    high_risk_customers = (
        db.query(Customer)
        .filter(Customer.health_score < 50)
        .order_by(Customer.id.asc())
        .all()
    )

    tasks_created = 0
    tasks_skipped = 0

    try:
        for customer in high_risk_customers:
            existing_task = (
                db.query(FollowUpTask)
                .filter(
                    FollowUpTask.customer_id == customer.id,
                    FollowUpTask.task_type
                    == AUTOMATED_RISK_REVIEW_TASK_TYPE,
                    FollowUpTask.status == "open",
                )
                .first()
            )

            if existing_task is not None:
                tasks_skipped += 1
                continue

            task = FollowUpTask(
                customer_id=customer.id,
                task_type=AUTOMATED_RISK_REVIEW_TASK_TYPE,
                recommended_action=build_automated_follow_up_action(
                    customer,
                    as_of=review_date,
                ),
                status="open",
                created_at=timestamp,
                updated_at=timestamp,
            )

            db.add(task)
            tasks_created += 1

        db.commit()
    except Exception:
        db.rollback()
        raise

    return RiskReviewResult(
        customers_scanned=customers_scanned,
        high_risk_customers=len(high_risk_customers),
        tasks_created=tasks_created,
        tasks_skipped=tasks_skipped,
    )