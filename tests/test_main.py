from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from models import Customer
from main import app
from database import get_db

from datetime import date, datetime, timezone

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_ticket():
    response = client.post(
        "/tickets",
        json={
            "title": "Test ticket",
            "description": "This ticket was created by pytest",
            "priority": "high",
            "status": "open"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Test ticket"
    assert data["priority"] == "high"
    assert data["status"] == "open"


def test_get_tickets():
    response = client.get("/tickets")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0


def test_get_ticket_by_id():
    create_response = client.post(
        "/tickets",
        json={
            "title": "Single ticket test",
            "description": "Testing GET by ID",
            "priority": "medium",
            "status": "open"
        }
    )

    ticket_id = create_response.json()["id"]

    response = client.get(f"/tickets/{ticket_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == ticket_id
    assert data["title"] == "Single ticket test"


def test_update_ticket():
    create_response = client.post(
        "/tickets",
        json={
            "title": "Single ticket test",
            "description": "Testing GET by ID",
            "priority": "medium",
            "status": "open"
        }
    )

    ticket_id = create_response.json()["id"]

    response = client.patch(
        f"/tickets/{ticket_id}",
        json={
            "status": "resolved"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == ticket_id
    assert data["status"] == "resolved"


def test_delete_ticket():
    create_response = client.post(
        "/tickets",
        json={
            "title": "Delete test",
            "description": "Testing DELETE",
            "priority": "low",
            "status": "open"
        }
    )

    ticket_id = create_response.json()["id"]

    delete_response = client.delete(f"/tickets/{ticket_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Ticket deleted"}

    get_response = client.get(f"/tickets/{ticket_id}")

    assert get_response.status_code == 404


def test_invalid_priority():
    response = client.post(
        "/tickets",
        json={
            "title": "Invalid priority test",
            "description": "Testing validation",
            "priority": "urgent",
            "status": "open"
        }
    )

    assert response.status_code == 422


def test_create_ticket_note():
    ticket_response = client.post(
        "/tickets",
        json={
            "title": "Payment issue",
            "description": "Customer cannot complete payment",
            "priority": "high",
        },
    )

    ticket_id = ticket_response.json()["id"]

    response = client.post(
        f"/tickets/{ticket_id}/notes",
        json={
            "content": "Issue reproduced in Chrome."
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert data["ticket_id"] == ticket_id
    assert data["content"] == "Issue reproduced in Chrome."


def test_get_ticket_notes():
    ticket_response = client.post(
        "/tickets",
        json={
            "title": "Login issue",
            "description": "Customer cannot log in",
            "priority": "medium",
        },
    )

    ticket_id = ticket_response.json()["id"]

    client.post(
        f"/tickets/{ticket_id}/notes",
        json={"content": "Reset password attempted."},
    )

    client.post(
        f"/tickets/{ticket_id}/notes",
        json={"content": "Escalated to engineering."},
    )

    response = client.get(f"/tickets/{ticket_id}/notes")

    assert response.status_code == 200

    notes = response.json()

    assert len(notes) == 2
    assert notes[0]["content"] == "Reset password attempted."
    assert notes[1]["content"] == "Escalated to engineering."


def test_create_note_for_missing_ticket():
    response = client.post(
        "/tickets/999999/notes",
        json={
            "content": "This note should not be created."
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_get_ticket_includes_notes():
    ticket_response = client.post(
        "/tickets",
        json={
            "title": "Checkout issue",
            "description": "Customer cannot complete checkout",
            "priority": "high",
        },
    )

    ticket_id = ticket_response.json()["id"]

    client.post(
        f"/tickets/{ticket_id}/notes",
        json={"content": "Issue reproduced on mobile."},
    )

    response = client.get(f"/tickets/{ticket_id}")

    assert response.status_code == 200

    data = response.json()

    assert "notes" in data
    assert len(data["notes"]) == 1
    assert data["notes"][0]["content"] == "Issue reproduced on mobile."


def test_ticket_pagination():
    for i in range(5):
        client.post(
            "/tickets",
            json={
                "title": f"Pagination Ticket {i}",
                "description": "Testing pagination",
                "priority": "low",
            },
        )

    response = client.get("/tickets?limit=2&offset=0")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_ticket_pagination_limit_validation():
    response = client.get("/tickets?limit=101")

    assert response.status_code == 422


def test_search_tickets():
    client.post(
        "/tickets",
        json={
            "title": "Stripe payment failure",
            "description": "Customer cannot complete checkout",
            "priority": "high",
        },
    )

    response = client.get("/tickets?search=Stripe")

    assert response.status_code == 200

    tickets = response.json()

    assert len(tickets) >= 1
    assert any(
        "Stripe" in ticket["title"]
        for ticket in tickets
    )


def test_sort_tickets_by_created_at_desc():
    response = client.get("/tickets?sort=-created_at")

    assert response.status_code == 200

    tickets = response.json()

    dates = [ticket["created_at"] for ticket in tickets]

    assert dates == sorted(dates, reverse=True)


def test_invalid_ticket_sort():
    response = client.get("/tickets?sort=banana")

    assert response.status_code == 422


def test_get_customers_with_ordering_and_filtering():
    now = datetime(2026, 9, 9, tzinfo=timezone.utc)

    risky_customer = Customer(
        name="Risky Customer Test",
        industry="fintech",
        account_owner="Jordan Lee",
        payment_volume=25000,
        payment_volume_change_30d=-30,
        product_usage=75,
        product_usage_change_30d=-25,
        open_support_tickets=5,
        last_login_at=now,
        features_adopted=3,
        total_available_features=10,
        renewal_date=date(2026, 11, 1),
        health_score=35,
        risk_level="high",
        created_at=now,
        updated_at=now,
    )

    healthy_customer = Customer(
        name="Healthy Customer Test",
        industry="insurance",
        account_owner="Morgan Smith",
        payment_volume=125000,
        payment_volume_change_30d=20,
        product_usage=500,
        product_usage_change_30d=15,
        open_support_tickets=0,
        last_login_at=now,
        features_adopted=9,
        total_available_features=10,
        renewal_date=date(2027, 3, 1),
        health_score=90,
        risk_level="healthy",
        created_at=now,
        updated_at=now,
    )

    db = TestingSessionLocal()

    try:
        db.add_all([risky_customer, healthy_customer])
        db.commit()

        response = client.get("/customers")

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 2
        assert data["items"][0]["name"] == "Risky Customer Test"
        assert data["items"][1]["name"] == "Healthy Customer Test"

        filtered_response = client.get(
            "/customers",
            params={"risk_level": "high"},
        )

        assert filtered_response.status_code == 200

        filtered_data = filtered_response.json()

        assert filtered_data["total"] == 1
        assert filtered_data["items"][0]["name"] == "Risky Customer Test"
    finally:
        db.query(Customer).filter(
            Customer.name.in_(
                ["Risky Customer Test", "Healthy Customer Test"]
            )
        ).delete(synchronize_session=False)
        db.commit()
        db.close()