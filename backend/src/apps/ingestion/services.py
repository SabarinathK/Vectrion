import io

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException, UploadFile
from pypdf import PdfReader
from sqlmodel import Session, delete, select

from src.apps.ingestion.models import KnowledgeChunk, KnowledgeSource
from src.platform.vectorstore.chroma_store import get_vector_store


class IngestionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_source(self, source: KnowledgeSource) -> KnowledgeSource:
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def get_source_by_id(self, source_id: int) -> KnowledgeSource | None:
        return self.db.exec(select(KnowledgeSource).where(KnowledgeSource.id == source_id)).first()

    def list_sources(self, user_id: int):
        return list(
            self.db.exec(
                select(KnowledgeSource)
                .where(KnowledgeSource.user_id == user_id)
                .order_by(KnowledgeSource.created_at.desc())
            ).all()
        )

    def update_source(self, source: KnowledgeSource) -> KnowledgeSource:
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def delete_source(self, source: KnowledgeSource) -> None:
        self.db.exec(delete(KnowledgeChunk).where(KnowledgeChunk.source_id == source.id))
        self.db.delete(source)
        self.db.commit()

    def bulk_create_chunks(self, chunks: list[KnowledgeChunk]) -> None:
        self.db.add_all(chunks)
        self.db.commit()

    def enqueue_processing(self, source_id: int) -> None:
        from src.apps.ingestion.tasks import process_source

        process_source.delay(source_id)

    def ingest_text(self, user_id: int, title: str, text: str) -> KnowledgeSource:
        source = self.create_source(
            KnowledgeSource(user_id=user_id, title=title, source_type="text", content=text, status="queued")
        )
        self.enqueue_processing(source.id)
        return source

    def ingest_url(self, user_id: int, title: str, url: str) -> KnowledgeSource:
        try:
            resp = httpx.get(url, timeout=20)
            resp.raise_for_status()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {exc}") from exc
        soup = BeautifulSoup(resp.text, "html.parser")
        text = "\n".join(x.get_text(" ", strip=True) for x in soup.find_all(["p", "h1", "h2", "h3", "li"]))
        source = self.create_source(
            KnowledgeSource(user_id=user_id, title=title, source_type="url", content=text, status="queued")
        )
        self.enqueue_processing(source.id)
        return source

    def ingest_file(self, user_id: int, title: str, file: UploadFile) -> KnowledgeSource:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        data = file.file.read()
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        source = self.create_source(
            KnowledgeSource(user_id=user_id, title=title, source_type="pdf", content=text, status="queued")
        )
        self.enqueue_processing(source.id)
        return source

    def remove_source(self, user_id: int, source_id: int) -> bool:
        source = self.get_source_by_id(source_id)
        if not source or source.user_id != user_id:
            raise HTTPException(status_code=404, detail="Source not found")
        get_vector_store().delete_by_source(user_id=user_id, source_id=source_id)
        self.delete_source(source)
        return True
