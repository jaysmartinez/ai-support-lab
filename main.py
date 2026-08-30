from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from enum import Enum
from datetime import datetime

from database import SessionLocal
from models import Ticket

app = FastAPI()

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class SupportTicketCreate(BaseModel):
    title: str
    description: str
    priority: Priority

class SupportTicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None


class SupportTicketResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: Priority
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "AI Support Lab API"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/tickets", status_code=201, response_model=SupportTicketResponse)
def create_ticket(
    ticket: SupportTicketCreate,
    db: Session = Depends(get_db),
):
    
    new_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket

@app.get("/tickets", response_model=list[SupportTicketResponse])
def get_tickets(
    priority: Optional[Priority] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Ticket)

    if priority:
        query = query.filter(Ticket.priority == priority.value)

    return query.all()


@app.get("/tickets/{ticket_id}", response_model=SupportTicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@app.patch("/tickets/{ticket_id}")
def update_ticket(
    ticket_id: int,
    updates: SupportTicketUpdate,
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    update_data = updates.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(ticket, key, value)

    db.commit()
    db.refresh(ticket)

    return ticket



@app.delete("/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()

    return {"message": "Ticket deleted"}
