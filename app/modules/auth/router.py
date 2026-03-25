from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.modules.auth.schemas import (
    RegisterRequest, LoginRequest,
    TokenResponse, RefreshRequest, UserResponse
)
from app.modules.auth import service

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if service.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    if service.get_user_by_username(db, payload.username):
        raise HTTPException(status_code=409, detail="Username already taken")
    return service.register_user(db, payload.email, payload.username, payload.password)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    access_token, refresh_token = service.login_user(db, payload.email, payload.password)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    access_token, refresh_token = service.refresh_tokens(db, payload.refresh_token)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", status_code=204)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    service.logout_user(db, payload.refresh_token)