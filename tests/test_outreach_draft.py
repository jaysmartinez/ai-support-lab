from datetime import date, datetime, timezone
from unittest.mock import Mock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from models import Customer, FollowUpTask, OutreachDraft
from services.outreach_draft import (
    OutreachDraftContent,
    build_outreach_prompt,
    create_outreach_draft,
    generate_outreach_draft,
)


def test_build_outreach_prompt_includes_customer_context_and_safety_rules():
    customer = Customer(
        name="Atlas Payments",
        industry="fintech",
        account_owner="Jordan Lee",
        health_score=35,
        risk_level="high",
        payment_volume_change_30d=-18.5,
        product_usage_change_30d=-12,
        open_support_tickets=4,
    )

    follow_up = FollowUpTask(
        recommended_action=(
            "Schedule a customer health review to discuss declining usage."
        ),
    )

    prompt = build_outreach_prompt(customer, follow_up)

    assert "Atlas Payments" in prompt
    assert "Jordan Lee" in prompt
    assert "-18.5%" in prompt
    assert "-12.0%" in prompt
    assert "4" in prompt
    assert follow_up.recommended_action in prompt

    assert "Do not mention the health score or risk level directly." in prompt
    assert "Do not invent facts, promises, discounts" in prompt
    assert "Keep the body under 180 words." in prompt


def test_generate_outreach_draft_uses_structured_openai_response():
    customer = Customer(
        name="Atlas Payments",
        industry="fintech",
        account_owner="Jordan Lee",
        health_score=35,
        risk_level="high",
        payment_volume_change_30d=-18.5,
        product_usage_change_30d=-12,
        open_support_tickets=4,
    )

    follow_up = FollowUpTask(
        recommended_action=(
            "Schedule a customer health review to discuss declining usage."
        ),
    )

    expected_draft = OutreachDraftContent(
        subject="Let’s review your Atlas Payments account",
        body=(
            "Hi Atlas Payments team,\n\n"
            "I’d like to schedule a short account review to discuss "
            "recent usage and any support needs.\n\n"
            "Best,\nJordan"
        ),
    )

    fake_client = Mock()
    fake_client.responses.parse.return_value.output_parsed = expected_draft

    result = generate_outreach_draft(
        customer,
        follow_up,
        client=fake_client,
        model="test-model",
    )

    assert result == expected_draft

    fake_client.responses.parse.assert_called_once()

    request = fake_client.responses.parse.call_args.kwargs

    assert request["model"] == "test-model"
    assert request["text_format"] is OutreachDraftContent
    assert "Atlas Payments" in request["input"]
    assert "Do not invent facts" in request["input"]


def test_create_outreach_draft_saves_and_reuses_existing_draft():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine)

    Base.metadata.create_all(bind=engine)
    db = testing_session()

    now = datetime(2026, 9, 21, tzinfo=timezone.utc)

    customer = Customer(
        name="Outreach Persistence Test",
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

    generated_content = OutreachDraftContent(
        subject="Let’s review your account",
        body="Hello, I would like to schedule a short account review.",
    )

    fake_client = Mock()
    fake_client.responses.parse.return_value.output_parsed = (
        generated_content
    )

    first_draft = create_outreach_draft(
        db,
        customer,
        follow_up,
        client=fake_client,
        model="test-model",
    )

    second_draft = create_outreach_draft(
        db,
        customer,
        follow_up,
        client=fake_client,
        model="test-model",
    )

    assert first_draft.id == second_draft.id
    assert first_draft.subject == generated_content.subject
    assert first_draft.body == generated_content.body
    assert first_draft.status == "draft"
    assert first_draft.model == "test-model"

    assert db.query(OutreachDraft).count() == 1
    fake_client.responses.parse.assert_called_once()

    db.close()
    Base.metadata.drop_all(bind=engine)