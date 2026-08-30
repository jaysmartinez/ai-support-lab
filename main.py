from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SupportTicket(BaseModel):
    title: str
    description: str
    priority:str

@app.get("/")
def root():
    return {"message": "AI Support Lab API"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/tickets")
def create_ticket(ticket: SupportTicket):
    return {
        "message": "Ticket recieved",
        "ticket": ticket
    }