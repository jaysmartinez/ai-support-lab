from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

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