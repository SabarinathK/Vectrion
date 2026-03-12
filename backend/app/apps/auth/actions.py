from sqlmodel import Session

from app.apps.auth.services import AuthService


def register_action(db: Session, email: str, full_name: str, password: str) -> str:
    return AuthService(db).register(email=email, full_name=full_name, password=password)


def login_action(db: Session, email: str, password: str) -> str:
    return AuthService(db).login(email=email, password=password)
