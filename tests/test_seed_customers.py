from collections import Counter
from datetime import date
from random import Random

from scripts.seed_customers import CUSTOMER_NAMES, build_customer_data


def test_seed_data_has_balanced_risk_distribution():
    today = date(2026, 9, 9)
    rng = Random(42)

    customers = [
        build_customer_data(index, today=today, rng=rng)
        for index in range(len(CUSTOMER_NAMES))
    ]

    risk_counts = Counter(
        customer["risk_level"]
        for customer in customers
    )

    assert len(customers) == 25
    assert len({customer["name"] for customer in customers}) == 25
    assert risk_counts == {
        "high": 8,
        "medium": 8,
        "healthy": 9,
    }

    assert all(
        0 <= customer["health_score"] <= 100
        for customer in customers
    )