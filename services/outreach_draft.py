from pydantic import BaseModel, Field
from models import Customer, FollowUpTask, OutreachDraft
import os

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from openai import OpenAI


class OutreachDraftContent(BaseModel):
    subject: str = Field(
        min_length=1,
        max_length=150,
    )
    body: str = Field(
        min_length=1,
        max_length=5000,
    )


def build_outreach_prompt(
    customer: Customer,
    follow_up: FollowUpTask,
) -> str:
    """Build the instructions and customer context for an outreach draft."""
    return f"""
Write a concise customer-success outreach email.

Customer:
- Name: {customer.name}
- Industry: {customer.industry}
- Account owner: {customer.account_owner}
- Health score: {customer.health_score}
- Risk level: {customer.risk_level}
- Payment volume change over 30 days: {customer.payment_volume_change_30d:.1f}%
- Product usage change over 30 days: {customer.product_usage_change_30d:.1f}%
- Open support tickets: {customer.open_support_tickets}
- Follow-up recommendation: {follow_up.recommended_action}

Requirements:
- Write from the account owner's perspective.
- Use a helpful, professional, and non-alarming tone.
- Do not mention the health score or risk level directly.
- Do not invent facts, promises, discounts, or customer quotes.
- Suggest a short account review meeting.
- Keep the body under 180 words.
- Return a subject and body.
""".strip()


def generate_outreach_draft(
    customer: Customer,
    follow_up: FollowUpTask,
    *,
    client: OpenAI | None = None,
    model: str | None = None,
) -> OutreachDraftContent:
    """Generate a validated outreach email draft."""
    openai_client = client or OpenAI()
    selected_model = model or os.getenv(
        "OPENAI_MODEL",
        "gpt-5-mini",
    )

    response = openai_client.responses.parse(
        model=selected_model,
        instructions=(
            "You are a customer-success assistant. "
            "Write accurate, empathetic outreach emails using only "
            "the supplied customer information."
        ),
        input=build_outreach_prompt(customer, follow_up),
        text_format=OutreachDraftContent,
    )

    draft = response.output_parsed

    if draft is None:
        raise ValueError(
            "OpenAI did not return a valid outreach draft."
        )

    return draft


def create_outreach_draft(
    db: Session,
    customer: Customer,
    follow_up: FollowUpTask,
    *,
    client: OpenAI | None = None,
    model: str | None = None,
) -> OutreachDraft:
    """Generate and save one outreach draft for a follow-up."""
    existing_draft = (
        db.query(OutreachDraft)
        .filter(
            OutreachDraft.follow_up_task_id == follow_up.id
        )
        .first()
    )

    if existing_draft is not None:
        return existing_draft

    selected_model = model or os.getenv(
        "OPENAI_MODEL",
        "gpt-5-mini",
    )

    content = generate_outreach_draft(
        customer,
        follow_up,
        client=client,
        model=selected_model,
    )

    now = datetime.now(timezone.utc)

    draft = OutreachDraft(
        follow_up_task_id=follow_up.id,
        subject=content.subject,
        body=content.body,
        status="draft",
        model=selected_model,
        created_at=now,
        updated_at=now,
    )

    db.add(draft)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(draft)

    return draft