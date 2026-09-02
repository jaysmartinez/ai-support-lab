from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from main import app
from database import get_db

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