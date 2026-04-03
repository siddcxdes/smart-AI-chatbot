from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    user_email: str
    question: str

class ChatResponse(BaseModel):
    answer: str
    source: str
    ticket_id: Optional[int] = None


class UserCreate(BaseModel):
    name: str
    email: str
    password: str  # users will send a plain password when they sign up

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str      # show if they are user or admin
    created_at: datetime

    class Config:
        from_attributes = True

# When a user logs in, we give them this token (like an entry ticket)
class Token(BaseModel):
    access_token: str
    token_type: str


class TicketResponse(BaseModel):
    id: int
    user_email: str
    question: str
    ai_response: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class TicketUpdate(BaseModel):
    status: str
