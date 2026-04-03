"""
auth.py - Simple security functions for letting users sign in
"""
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User

# A secret password that only our server knows.
# It uses this to stamp/sign the tokens so nobody can fake them.
SECRET_KEY = "my_super_secret_chatbot_key" 

# We use bcrypt - it's the industry standard for safe passwords.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Tells the app that the "Login Page" is at /api/users/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    This function looks at the 'wristband' (token), checks if it's real,
    and then gives us the exact User from the database.
    """
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    try:
        # Check the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise error
            
        # Is it the master admin bypass code?
        if email == "master-admin@resolv.ai" and payload.get("role") == "admin":
            # Just create a fake User object on the spot so FastAPI dependencies don't crash
            return User(id=9999, email="master-admin@resolv.ai", role="admin", name="Master Admin", created_at=datetime.utcnow())
            
    except Exception:
        raise error
        
    # Find the user in the database
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise error
        
    return user


def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    Extra security check: It gets the user, then checks if their role is 'admin'.
    If not, it blocks them with a Forbidden error.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not an admin! Access denied."
        )
    return current_user


def hash_password(password: str):
    """Takes a plain password ('1234') and turns it into a scrambled mess."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """Checks if the typed password matches the scrambled one in the database."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """
    Creates a 'Digital Wristband' (JWT token).
    When users log in successfully, we give them this token.
    They show it on later requests so we know who they are.
    """
    to_encode = data.copy()
    
    # Token is valid for 1 hour (60 minutes)
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    
    # Create the stamped token string
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
