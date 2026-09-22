from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from database import get_db
from models import Customer, FollowUpTask, OutreachDraft
from schemas import (
    CustomerListResponse,
    CustomerResponse,
    CustomerSummaryResponse,
    FollowUpTaskCreate,
    FollowUpTaskResponse,
    OutreachDraftResponse,
    RiskReviewResponse,
    OutreachDraftUpdate,
)
from services.health_score import RiskLevel
from services.risk_automation import run_risk_review
from services.outreach_draft import create_outreach_draft


router = APIRouter(
    prefix="/customers",
    tags=["customers"],
)


@router.get("", response_model=CustomerListResponse)
def get_customers(
    risk_level: Optional[RiskLevel] = None,
    search: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Customer)

    if risk_level is not None:
        query = query.filter(
            Customer.risk_level == risk_level.value
        )

    if search:
        query = query.filter(
            Customer.name.ilike(f"%{search}%")
        )

    total = query.count()

    customers = (
        query.order_by(
            Customer.health_score.asc(),
            Customer.name.asc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "items": customers,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/summary",
    response_model=CustomerSummaryResponse,
)
def get_customer_summary(
    db: Session = Depends(get_db),
):
    summary = db.query(
        func.count(Customer.id).label("total"),
        func.sum(
            case(
                (Customer.risk_level == "high", 1),
                else_=0,
            )
        ).label("high_risk"),
        func.sum(
            case(
                (Customer.risk_level == "medium", 1),
                else_=0,
            )
        ).label("medium_risk"),
        func.sum(
            case(
                (Customer.risk_level == "healthy", 1),
                else_=0,
            )
        ).label("healthy"),
    ).one()

    return {
        "total_customers": summary.total or 0,
        "high_risk_customers": summary.high_risk or 0,
        "medium_risk_customers": summary.medium_risk or 0,
        "healthy_customers": summary.healthy or 0,
    }

@router.post(
    "/risk-review",
    response_model=RiskReviewResponse,
)
def create_risk_review(
    db: Session = Depends(get_db),
):
    result = run_risk_review(db)

    return {
        "customers_scanned": result.customers_scanned,
        "high_risk_customers": result.high_risk_customers,
        "tasks_created": result.tasks_created,
        "tasks_skipped": result.tasks_skipped,
    }

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer

@router.post(
    "/{customer_id}/follow-ups",
    status_code=201,
    response_model=FollowUpTaskResponse,
)
def create_follow_up(
    customer_id: int,
    task: FollowUpTaskCreate,
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    if customer.health_score >= 50:
        raise HTTPException(
            status_code=409,
            detail="Follow-up creation requires a health score below 50",
        )

    now = datetime.now(timezone.utc)

    new_task = FollowUpTask(
        customer_id=customer.id,
        task_type=task.task_type,
        recommended_action=task.recommended_action,
        status="open",
        created_at=now,
        updated_at=now,
    )

    db.add(new_task)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(new_task)

    return new_task

@router.get(
    "/{customer_id}/follow-ups",
    response_model=list[FollowUpTaskResponse],
)
def get_customer_follow_ups(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return (
        db.query(FollowUpTask)
        .filter(FollowUpTask.customer_id == customer_id)
        .order_by(
            FollowUpTask.created_at.desc(),
            FollowUpTask.id.desc(),
        )
        .all()
    )

@router.patch(
    "/{customer_id}/follow-ups/{task_id}/outreach-draft",
    response_model=OutreachDraftResponse,
)
def update_customer_outreach_draft(
    customer_id: int,
    task_id: int,
    changes: OutreachDraftUpdate,
    db: Session = Depends(get_db),
):
    draft = (
        db.query(OutreachDraft)
        .join(FollowUpTask)
        .filter(
            FollowUpTask.id == task_id,
            FollowUpTask.customer_id == customer_id,
            OutreachDraft.follow_up_task_id == task_id,
        )
        .first()
    )

    if draft is None:
        raise HTTPException(
            status_code=404,
            detail="Outreach draft not found",
        )

    if draft.status != "draft":
        raise HTTPException(
            status_code=409,
            detail="Only drafts can be edited",
        )

    draft.subject = changes.subject
    draft.body = changes.body
    draft.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(draft)
    return draft

@router.patch(
    "/{customer_id}/follow-ups/{task_id}/outreach-draft/approve",
    response_model=OutreachDraftResponse,
)
def approve_customer_outreach_draft(
    customer_id: int,
    task_id: int,
    db: Session = Depends(get_db),
):
    draft = (
        db.query(OutreachDraft)
        .join(FollowUpTask)
        .filter(
            FollowUpTask.id == task_id,
            FollowUpTask.customer_id == customer_id,
            OutreachDraft.follow_up_task_id == task_id,
        )
        .first()
    )

    if draft is None:
        raise HTTPException(
            status_code=404,
            detail="Outreach draft not found",
        )

    if draft.status != "draft":
        raise HTTPException(
            status_code=409,
            detail="Only drafts can be approved",
        )

    draft.status = "approved"
    draft.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(draft)
    return draft

@router.post(
    "/{customer_id}/follow-ups/{task_id}/outreach-draft",
    response_model=OutreachDraftResponse,
)
def generate_customer_outreach_draft(
    customer_id: int,
    task_id: int,
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    follow_up = (
        db.query(FollowUpTask)
        .filter(
            FollowUpTask.id == task_id,
            FollowUpTask.customer_id == customer_id,
        )
        .first()
    )

    if follow_up is None:
        raise HTTPException(
            status_code=404,
            detail="Follow-up not found",
        )

    return create_outreach_draft(
        db,
        customer,
        follow_up,
    )


@router.patch(
    "/{customer_id}/follow-ups/{task_id}/complete",
    response_model=FollowUpTaskResponse,
)
def complete_customer_follow_up(
    customer_id: int,
    task_id: int,
    db: Session = Depends(get_db),
):
    task = (
        db.query(FollowUpTask)
        .filter(
            FollowUpTask.id == task_id,
            FollowUpTask.customer_id == customer_id,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Follow-up not found",
        )

    task.status = "completed"
    task.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(task)

    return task