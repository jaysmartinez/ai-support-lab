from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from models import Customer, FollowUpTask, OutreachDraft
from main import app
from database import get_db

from datetime import date, datetime, timezone

from unittest.mock import patch

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


def test_cors_allows_frontend_patch_requests():
    response = client.options(
        "/customers/1/follow-ups/1/complete",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "PATCH",
        },
    )

    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "http://localhost:3000"
    )
    assert "PATCH" in response.headers["access-control-allow-methods"]


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

        detail_response = client.get(
            f"/customers/{risky_customer.id}"
        )

        assert detail_response.status_code == 200

        detail_data = detail_response.json()

        assert detail_data["id"] == risky_customer.id
        assert detail_data["name"] == "Risky Customer Test"
        assert detail_data["health_score"] == 35
        assert detail_data["risk_level"] == "high"

        missing_response = client.get("/customers/999999")

        assert missing_response.status_code == 404
        assert missing_response.json() == {
            "detail": "Customer not found"
        }

        summary_response = client.get("/customers/summary")

        assert summary_response.status_code == 200
        assert summary_response.json() == {
            "total_customers": 2,
            "high_risk_customers": 1,
            "medium_risk_customers": 0,
            "healthy_customers": 1,
        }

        task_payload = {
            "task_type": "account_health_check",
            "recommended_action": "Schedule a customer health review.",
        }

        create_response = client.post(
            f"/customers/{risky_customer.id}/follow-ups",
            json=task_payload,
        )

        assert create_response.status_code == 201

        task_data = create_response.json()

        assert task_data["customer_id"] == risky_customer.id
        assert task_data["task_type"] == "account_health_check"
        assert task_data["status"] == "open"
        assert task_data["recommended_action"] == (
            "Schedule a customer health review."
        )

        ineligible_response = client.post(
            f"/customers/{healthy_customer.id}/follow-ups",
            json=task_payload,
        )

        assert ineligible_response.status_code == 409

        missing_customer_response = client.post(
            "/customers/999999/follow-ups",
            json=task_payload,
        )

        assert missing_customer_response.status_code == 404

        follow_ups_response = client.get(
            f"/customers/{risky_customer.id}/follow-ups"
        )

        assert follow_ups_response.status_code == 200

        follow_ups = follow_ups_response.json()

        assert len(follow_ups) == 1
        assert follow_ups[0]["id"] == task_data["id"]
        assert follow_ups[0]["customer_id"] == risky_customer.id
        assert follow_ups[0]["recommended_action"] == (
            task_payload["recommended_action"]
        )
        assert follow_ups[0]["status"] == "open"

        empty_response = client.get(
            f"/customers/{healthy_customer.id}/follow-ups"
        )

        assert empty_response.status_code == 200
        assert empty_response.json() == []

        missing_follow_ups_response = client.get(
            "/customers/999999/follow-ups"
        )

        assert missing_follow_ups_response.status_code == 404
        assert missing_follow_ups_response.json() == {
            "detail": "Customer not found"
        }

        wrong_customer_response = client.patch(
            f"/customers/{healthy_customer.id}"
            f"/follow-ups/{task_data['id']}/complete"
        )

        assert wrong_customer_response.status_code == 404
        assert wrong_customer_response.json() == {
            "detail": "Follow-up not found"
        }

        complete_response = client.patch(
            f"/customers/{risky_customer.id}"
            f"/follow-ups/{task_data['id']}/complete"
        )

        assert complete_response.status_code == 200

        completed_task = complete_response.json()

        assert completed_task["id"] == task_data["id"]
        assert completed_task["customer_id"] == risky_customer.id
        assert completed_task["status"] == "completed"
        assert completed_task["updated_at"] >= task_data["updated_at"]

        completed_list_response = client.get(
            f"/customers/{risky_customer.id}/follow-ups"
        )

        assert completed_list_response.status_code == 200
        assert completed_list_response.json()[0]["status"] == "completed"

    finally:
        test_customers = db.query(Customer).filter(
            Customer.name.in_(
                ["Risky Customer Test", "Healthy Customer Test"]
            )
        ).all()

        for customer in test_customers:
            db.delete(customer)

        db.commit()
        db.close()


def test_run_risk_review_endpoint_prevents_duplicate_tasks():
    now = datetime(2026, 9, 21, tzinfo=timezone.utc)

    customer = Customer(
        name="Risk Review Endpoint Test",
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
        created_at=now,
        updated_at=now,
    )

    db = TestingSessionLocal()

    try:
        db.add(customer)
        db.commit()
        db.refresh(customer)

        first_response = client.post("/customers/risk-review")

        assert first_response.status_code == 200
        assert first_response.json() == {
            "customers_scanned": 1,
            "high_risk_customers": 1,
            "tasks_created": 1,
            "tasks_skipped": 0,
        }

        second_response = client.post("/customers/risk-review")

        assert second_response.status_code == 200
        assert second_response.json() == {
            "customers_scanned": 1,
            "high_risk_customers": 1,
            "tasks_created": 0,
            "tasks_skipped": 1,
        }

        tasks = (
            db.query(FollowUpTask)
            .filter(FollowUpTask.customer_id == customer.id)
            .all()
        )

        assert len(tasks) == 1
        assert tasks[0].task_type == "automated_risk_review"
        assert tasks[0].status == "open"
    finally:
        db.query(FollowUpTask).filter(
            FollowUpTask.customer_id == customer.id
        ).delete()

        db.query(Customer).filter(
            Customer.id == customer.id
        ).delete()

        db.commit()
        db.close()


def test_generate_outreach_draft_endpoint():
    now = datetime(2026, 9, 21, tzinfo=timezone.utc)

    customer = Customer(
        name="Outreach Endpoint Test",
        industry="fintech",
        account_owner="Jordan Lee",
        payment_volume=25000,
        payment_volume_change_30d=-18.5,
        product_usage=80,
        product_usage_change_30d=-12,
        open_support_tickets=4,
        last_login_at=now,
        features_adopted=3,
        total_available_features=10,
        renewal_date=date(2026, 10, 15),
        health_score=35,
        risk_level="high",
        created_at=now,
        updated_at=now,
    )

    db = TestingSessionLocal()

    try:
        db.add(customer)
        db.commit()
        db.refresh(customer)

        follow_up = FollowUpTask(
            customer_id=customer.id,
            task_type="automated_risk_review",
            recommended_action="Schedule a customer health review.",
            status="open",
            created_at=now,
            updated_at=now,
        )

        db.add(follow_up)
        db.commit()
        db.refresh(follow_up)

        saved_draft = {
            "id": 1,
            "follow_up_task_id": follow_up.id,
            "subject": "Let’s review your account",
            "body": (
                "Hello, I would like to schedule a short account review."
            ),
            "status": "draft",
            "model": "test-model",
            "created_at": now,
            "updated_at": now,
        }

        with patch(
            "routers.customers.create_outreach_draft",
            return_value=saved_draft,
        ) as create_mock:
            response = client.post(
                f"/customers/{customer.id}"
                f"/follow-ups/{follow_up.id}/outreach-draft"
            )

        assert response.status_code == 200
        assert response.json()["subject"] == saved_draft["subject"]
        assert response.json()["body"] == saved_draft["body"]
        assert response.json()["status"] == "draft"
        assert response.json()["follow_up_task_id"] == follow_up.id

        create_mock.assert_called_once()

        draft = OutreachDraft(
            follow_up_task_id=follow_up.id,
            subject="Original subject",
            body="Original body",
            status="draft",
            model="test-model",
            created_at=now,
            updated_at=now,
        )
        db.add(draft)
        db.commit()

        draft_url = (
            f"/customers/{customer.id}"
            f"/follow-ups/{follow_up.id}/outreach-draft"
        )

        update_response = client.patch(
            draft_url,
            json={
                "subject": "Revised subject",
                "body": "Hello, could we schedule a short review?",
            },
        )

        assert update_response.status_code == 200
        assert update_response.json()["subject"] == "Revised subject"
        assert update_response.json()["body"] == (
            "Hello, could we schedule a short review?"
        )

        blank_response = client.patch(
            draft_url,
            json={"subject": "   ", "body": "Valid body"},
        )
        assert blank_response.status_code == 422

        approve_response = client.patch(f"{draft_url}/approve")
        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "approved"
        assert approve_response.json()["approved_at"] is not None

        approve_again_response = client.patch(f"{draft_url}/approve")
        assert approve_again_response.status_code == 409

        locked_response = client.patch(
            draft_url,
            json={"subject": "Another subject", "body": "Another body"},
        )
        assert locked_response.status_code == 409

    finally:
        db.query(OutreachDraft).filter(
            OutreachDraft.follow_up_task_id == follow_up.id
        ).delete()

        db.query(FollowUpTask).filter(
            FollowUpTask.customer_id == customer.id
        ).delete()

        db.query(Customer).filter(
            Customer.id == customer.id
        ).delete()

        db.commit()
        db.close()