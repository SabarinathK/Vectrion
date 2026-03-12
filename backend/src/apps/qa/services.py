from sqlmodel import Session

from src.apps.qa.models import QALog
from src.platform.llm.langgraph_rag import ask_rag
from src.platform.vectorstore.chroma_store import get_vector_store


class QAService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_log(self, user_id: int, question: str, answer: str) -> QALog:
        log = QALog(user_id=user_id, question=question, answer=answer)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def ask(self, user_id: int, question: str) -> str:
        docs = get_vector_store().similarity_search(
            user_id=user_id, query=question, k=5
        )
        print(docs)
        answer = ask_rag(question=question, docs=docs)
        self.create_log(user_id=user_id, question=question, answer=answer)
        return answer
