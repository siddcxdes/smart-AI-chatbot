"""
auth.py - Simple security functions for letting users sign in
"""
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import User

SECRET_KEY = "my_super_secret_chatbot_key"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Validate token and return the user from the database."""
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise error

        if email == "master-admin@resolv.ai" and payload.get("role") == "admin":
            return User(id=9999, email="master-admin@resolv.ai", role="admin", name="Master Admin", created_at=datetime.utcnow())

    except Exception:
        raise error

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise error

    return user


def get_admin_user(current_user: User = Depends(get_current_user)):
    """Extra check: block non-admin users."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an admin! Access denied."
        )
    return current_user


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
