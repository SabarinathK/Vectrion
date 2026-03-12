from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.apps.auth.services import AuthService
from src.apps.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from src.common.deps import get_db

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    token = AuthService(db).register(payload.email, payload.full_name, payload.password)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = AuthService(db).login(payload.email, payload.password)
    return TokenResponse(access_token=token)
