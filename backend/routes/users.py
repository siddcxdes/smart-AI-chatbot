from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.schemas import UserCreate, UserResponse, Token
from backend.db.models import User
from backend.auth import hash_password, verify_password, create_access_token, get_admin_user, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
import os

router = APIRouter()

class AdminSecretLogin(BaseModel):
    secret_code: str


@router.post("/users/signup", response_model=UserResponse)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Oops, a user with this email already exists.")

    scrambled_pwd = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=scrambled_pwd,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/users/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/users/admin-secret-login", response_model=Token)
def admin_secret_login(data: AdminSecretLogin):
    expected_secret = os.getenv("ADMIN_SECRET_CODE")
    if not expected_secret or data.secret_code != expected_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Secret Code"
        )

    token = create_access_token(data={"sub": "master-admin@resolv.ai", "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    return db.query(User).all()

@router.get("/users/{email}", response_model=UserResponse)
def get_user(email: str, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
