from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    category = Column(String(100), nullable=True)


class TicketNote(Base):
    __tablename__ = "ticket_notes"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id"),
        nullable=False,
    )

    content = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )