from fastapi import HTTPException, status
from sqlmodel import Session

from app.apps.auth.models import User
from app.apps.auth.repositories import UserRepository
from app.common.security import create_access_token, get_password_hash, verify_password


class AuthService:
    def __init__(self, db: Session) -> None:
        self.repo = UserRepository(db)

    def register(self, email: str, full_name: str, password: str) -> str:
        if self.repo.get_by_email(email):
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(email=email, full_name=full_name, hashed_password=get_password_hash(password))
        user = self.repo.create(user)
        return create_access_token(str(user.id))

    def login(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return create_access_token(str(user.id))
