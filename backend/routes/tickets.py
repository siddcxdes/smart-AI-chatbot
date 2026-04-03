from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import TicketResponse, TicketUpdate
from backend.models import SupportTicket, User
from backend.auth import get_admin_user

router = APIRouter()

# Notice `admin: User = Depends(get_admin_user)`!
# It acts like a bouncer. If they aren't admin, it blocks the code from even running.
@router.get("/tickets", response_model=list[TicketResponse])
def get_all_tickets(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    tickets = db.query(SupportTicket).order_by(
        SupportTicket.created_at.desc()
    ).all()
    return tickets


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, update: TicketUpdate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    allowed = ["open", "in_progress", "closed"]
    if update.status not in allowed:
        raise HTTPException(status_code=400, detail="Status must be: open, in_progress, or closed")

    ticket.status = update.status
    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()
    return {"message": "Ticket deleted"}
