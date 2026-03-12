from sqlmodel import Session

from app.apps.qa.services import QAService


def ask_action(db: Session, user_id: int, question: str) -> str:
    return QAService(db).ask(user_id=user_id, question=question)
