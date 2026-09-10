from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from random import Random

from database import SessionLocal
from models import Customer
from services.health_score import HealthMetrics, calculate_health_score


CUSTOMER_NAMES = [
    "Atlas Payments",
    "Beacon Mutual",
    "BluePeak Finance",
    "Cedar Insurance",
    "Clearwater Capital",
    "Copperline Bank",
    "Evergreen Benefits",
    "Frontier Payments",
    "Granite Financial",
    "Harbor Risk",
    "Juniper Credit",
    "Lakeview Insurance",
    "MaplePay",
    "Meridian Lending",
    "Northstar Coverage",
    "Oakline Finance",
    "Pioneer Mutual",
    "Prairie Payments",
    "Redwood Assurance",
    "Riverbend Credit",
    "Silverline Financial",
    "Summit Insurance",
    "Timberland Payments",
    "Union Harbor Bank",
    "Westfield Benefits",
]

ACCOUNT_OWNERS = [
    "Jordan Lee",
    "Morgan Smith",
    "Taylor Patel",
    "Casey Nguyen",
    "Riley Johnson",
]

INDUSTRIES = ["fintech", "insurance"]


def build_customer_data(
    index: int,
    *,
    today: date,
    rng: Random,
) -> dict:
    if index < 8:
        payment_change = rng.uniform(-29, -5)
        usage_change = rng.uniform(-29, -5)
        open_tickets = rng.randint(2, 4)
        days_since_login = rng.randint(14, 45)
        features_adopted = rng.randint(3, 5)
    elif index < 17:
        payment_change = rng.uniform(-10, 10)
        usage_change = rng.uniform(-10, 10)
        open_tickets = rng.randint(1, 2)
        days_since_login = rng.randint(7, 25)
        features_adopted = rng.randint(5, 7)
    else:
        payment_change = rng.uniform(5, 30)
        usage_change = rng.uniform(5, 30)
        open_tickets = 0
        days_since_login = rng.randint(0, 7)
        features_adopted = rng.randint(8, 10)

    total_features = 10
    last_login_at = datetime.combine(
        today - timedelta(days=days_since_login),
        time(hour=14),
        tzinfo=timezone.utc,
    )

    metrics = HealthMetrics(
        payment_volume_change_30d=payment_change,
        product_usage_change_30d=usage_change,
        open_support_tickets=open_tickets,
        last_login_at=last_login_at,
        features_adopted=features_adopted,
        total_available_features=total_features,
    )

    assessment = calculate_health_score(metrics, as_of=today)
    now = datetime.now(timezone.utc)

    return {
        "name": CUSTOMER_NAMES[index],
        "industry": INDUSTRIES[index % len(INDUSTRIES)],
        "account_owner": ACCOUNT_OWNERS[index % len(ACCOUNT_OWNERS)],
        "payment_volume": Decimal(rng.randint(10_000, 500_000)),
        "payment_volume_change_30d": round(payment_change, 2),
        "product_usage": rng.randint(50, 2_000),
        "product_usage_change_30d": round(usage_change, 2),
        "open_support_tickets": open_tickets,
        "last_login_at": last_login_at,
        "features_adopted": features_adopted,
        "total_available_features": total_features,
        "renewal_date": today + timedelta(days=rng.randint(15, 365)),
        "health_score": assessment.score,
        "risk_level": assessment.risk_level.value,
        "created_at": now,
        "updated_at": now,
    }


def seed_customers() -> None:
    today = date.today()
    rng = Random(42)
    db = SessionLocal()

    try:
        existing_names = {
            name
            for (name,) in db.query(Customer.name).all()
        }

        customers = [
            Customer(**build_customer_data(index, today=today, rng=rng))
            for index in range(len(CUSTOMER_NAMES))
            if CUSTOMER_NAMES[index] not in existing_names
        ]

        db.add_all(customers)
        db.commit()

        print(f"Created {len(customers)} customers.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_customers()