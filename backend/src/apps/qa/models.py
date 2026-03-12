from datetime import datetime

from sqlmodel import Field, SQLModel


class QALog(SQLModel, table=True):
    __tablename__ = "qa_logs"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    question: str
    answer: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
