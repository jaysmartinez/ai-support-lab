from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from typing import Optional

from database import get_db
from models import Ticket
from schemas import (
    Priority,
    TicketStatus,
    SupportTicketCreate,
    SupportTicketUpdate,
    SupportTicketResponse,
)

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


@router.post("", status_code=201, response_model=SupportTicketResponse)
def create_ticket(
    ticket: SupportTicketCreate,
    db: Session = Depends(get_db),
):
    
    new_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority.value,
        status=ticket.status.value,
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket

@router.get("", response_model=list[SupportTicketResponse])
def get_tickets(
    priority: Optional[Priority] = None,
    status: Optional[TicketStatus] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Ticket)

    if priority:
        query = query.filter(Ticket.priority == priority.value)

    if status:
        query = query.filter(Ticket.status == status.value)

    return query.all()


@router.get("/{ticket_id}", response_model=SupportTicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.patch("/{ticket_id}", response_model=SupportTicketResponse)
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



@router.delete("/{ticket_id}")
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
