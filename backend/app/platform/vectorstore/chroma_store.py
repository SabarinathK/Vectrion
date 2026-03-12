import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.common.config import get_settings

settings = get_settings()


class ChromaStore:
    def __init__(self) -> None:
        os.makedirs(settings.chroma_persist_directory, exist_ok=True)
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.gemini_embed_model,
            google_api_key=settings.gemini_api_key,
        )
        self.db = Chroma(
            collection_name=settings.chroma_collection_name,
            persist_directory=settings.chroma_persist_directory,
            embedding_function=embeddings,
        )

    def add_chunks(self, user_id: int, source_id: int, chunks: list[str]) -> None:
        docs = [
            Document(
                page_content=chunk,
                metadata={
                    "user_id": str(user_id),
                    "source_id": str(source_id),
                    "chunk_index": i,
                },
            )
            for i, chunk in enumerate(chunks)
            if chunk.strip()
        ]
        if docs:
            self.db.add_documents(docs)

    def similarity_search(self, user_id: int, query: str, k: int = 5):
        return self.db.similarity_search(query, k=k, filter={"user_id": str(user_id)})

    def delete_by_source(self, user_id: int, source_id: int) -> None:
        self.db.delete(
            where={"$and": [{"user_id": str(user_id)}, {"source_id": str(source_id)}]}
        )


_vector_store: ChromaStore | None = None


def get_vector_store() -> ChromaStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = ChromaStore()
    return _vector_store
