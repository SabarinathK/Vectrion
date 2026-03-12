from sqlmodel import Session

from app.apps.qa.models import QALog


class QARepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_log(self, user_id: int, question: str, answer: str) -> QALog:
        log = QALog(user_id=user_id, question=question, answer=answer)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
