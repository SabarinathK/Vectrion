from sqlmodel import Session

from app.apps.qa.repositories import QARepository
from app.platform.llm.langgraph_rag import ask_rag
from app.platform.vectorstore.chroma_store import get_vector_store


class QAService:
    def __init__(self, db: Session) -> None:
        self.repo = QARepository(db)

    def ask(self, user_id: int, question: str) -> str:
        docs = get_vector_store().similarity_search(user_id=user_id, query=question, k=5)
        answer = ask_rag(question=question, docs=docs)
        self.repo.create_log(user_id=user_id, question=question, answer=answer)
        return answer
