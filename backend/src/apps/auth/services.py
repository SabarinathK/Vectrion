from fastapi import HTTPException, status
from sqlmodel import Session, select

from src.apps.auth.models import User
from src.common.security import create_access_token, get_password_hash, verify_password


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.exec(select(User).where(User.id == user_id)).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.exec(select(User).where(User.email == email)).first()

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def register(self, email: str, full_name: str, password: str) -> str:
        if self.get_by_email(email):
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(email=email, full_name=full_name, hashed_password=get_password_hash(password))
        user = self.create_user(user)
        return create_access_token(str(user.id))

    def login(self, email: str, password: str) -> str:
        user = self.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return create_access_token(str(user.id))
