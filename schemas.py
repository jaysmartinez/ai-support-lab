from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from services.health_score import RiskLevel

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"

class SupportTicketCreate(BaseModel):
    title: str
    description: str
    priority: Priority
    status: TicketStatus = TicketStatus.open

class SupportTicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[TicketStatus] = None

class SupportTicketResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: Priority
    status: TicketStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class TicketNoteCreate(BaseModel):
    content: str


class TicketNoteResponse(BaseModel):
    id: int
    ticket_id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SupportTicketWithNotes(SupportTicketResponse):
    notes: list[TicketNoteResponse] = []

    model_config = {"from_attributes": True}


class TicketSort(str, Enum):
    created_at = "created_at"
    created_at_desc = "-created_at"
    priority = "priority"


class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerResponse(BaseModel):
    id: int
    name: str
    industry: str
    account_owner: str

    payment_volume: Decimal
    payment_volume_change_30d: float

    product_usage: int
    product_usage_change_30d: float

    open_support_tickets: int
    last_login_at: datetime

    features_adopted: int
    total_available_features: int

    renewal_date: date
    health_score: int
    risk_level: RiskLevel

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    limit: int
    offset: int


class CustomerSummaryResponse(BaseModel):
    total_customers: int
    high_risk_customers: int
    medium_risk_customers: int
    healthy_customers: int


class FollowUpStatus(str, Enum):
    open = "open"
    completed = "completed"
    cancelled = "cancelled"


class FollowUpTaskCreate(BaseModel):
    task_type: str = Field(
        min_length=1,
        max_length=100,
    )
    recommended_action: str = Field(
        min_length=1,
        max_length=2000,
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )


class FollowUpTaskResponse(BaseModel):
    id: int
    customer_id: int
    task_type: str
    recommended_action: str
    status: FollowUpStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RiskReviewResponse(BaseModel):
    customers_scanned: int
    high_risk_customers: int
    tasks_created: int
    tasks_skipped: int


class OutreachDraftResponse(BaseModel):
    id: int
    follow_up_task_id: int
    subject: str
    body: str
    status: str
    model: str
    created_at: datetime
    updated_at: datetime
    approved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class OutreachDraftUpdate(BaseModel):
    subject: str = Field(min_length=1, max_length=150)
    body: str = Field(min_length=1, max_length=5000)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )
