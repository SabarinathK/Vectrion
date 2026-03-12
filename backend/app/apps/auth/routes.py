from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.apps.auth.actions import login_action, register_action
from app.apps.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.common.deps import get_db

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    token = register_action(db, payload.email, payload.full_name, payload.password)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = login_action(db, payload.email, payload.password)
    return TokenResponse(access_token=token)
