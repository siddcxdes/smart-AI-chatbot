from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from backend.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(250), nullable=False)
    role = Column(String(50), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(150), nullable=False)
    question = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=True)
    status = Column(String(50), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(150), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    was_helpful = Column(String(10), default="unknown")
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    """Stores uploaded document text content in PostgreSQL for deployment."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    file_type = Column(String(10), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
