from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import UserCreate, UserResponse, Token
from backend.models import User
from backend.auth import hash_password, verify_password, create_access_token, get_admin_user, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
import os

router = APIRouter()

class AdminSecretLogin(BaseModel):
    secret_code: str



@router.post("/users/signup", response_model=UserResponse)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    """User gives name, email, and password to create an account."""
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Oops, a user with this email already exists.")

    # 1. Scramble the password so hackers can't read it if database leaks
    scrambled_pwd = hash_password(user.password)

    # 2. Create the user object. Default they become a regular "user"
    new_user = User(
        name=user.name, 
        email=user.email, 
        hashed_password=scrambled_pwd,
        role="user"  # "admin" status has to be given manually or checking a special list
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/users/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Users type email and password.
    If it's right, we give them an Access Token (Digital VIP wristband).
    """
    # Look them up by email (FastAPI OAuth uses 'username' instead of 'email' but it means the same thing)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # If no email, or password doesn't match...
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create their special token and stamp it with their email and role!
    token = create_access_token(data={"sub": user.email, "role": user.role})
    
    return {"access_token": token, "token_type": "bearer"}


@router.post("/users/admin-secret-login", response_model=Token)
def admin_secret_login(data: AdminSecretLogin):
    """
    Hidden admin login! Enter the secret code to instantly get an admin token.
    """
    expected_secret = os.getenv("ADMIN_SECRET_CODE")
    if not expected_secret or data.secret_code != expected_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Secret Code"
        )
    
    # Issue a special "Master Admin" token
    token = create_access_token(data={"sub": "master-admin@resolv.ai", "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """A logged-in user can check their own profile."""
    return current_user

@router.get("/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """Only an admin can get a list of ALL users."""
    return db.query(User).all()

@router.get("/users/{email}", response_model=UserResponse)
def get_user(email: str, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    """Only an admin can search up an exact user."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
