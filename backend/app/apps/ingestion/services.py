import io

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException, UploadFile
from pypdf import PdfReader
from sqlmodel import Session

from app.apps.ingestion.models import KnowledgeSource
from app.apps.ingestion.repositories import SourceRepository
from app.platform.tasks.worker import process_source
from app.platform.vectorstore.chroma_store import get_vector_store


class IngestionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SourceRepository(db)

    def list_sources(self, user_id: int):
        return self.repo.list_by_user(user_id)

    def ingest_text(self, user_id: int, title: str, text: str) -> KnowledgeSource:
        source = self.repo.create(
            KnowledgeSource(user_id=user_id, title=title, source_type="text", content=text, status="queued")
        )
        process_source.delay(source.id)
        return source

    def ingest_url(self, user_id: int, title: str, url: str) -> KnowledgeSource:
        try:
            resp = httpx.get(url, timeout=20)
            resp.raise_for_status()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {exc}") from exc
        soup = BeautifulSoup(resp.text, "html.parser")
        text = "\n".join(x.get_text(" ", strip=True) for x in soup.find_all(["p", "h1", "h2", "h3", "li"]))
        source = self.repo.create(
            KnowledgeSource(user_id=user_id, title=title, source_type="url", content=text, status="queued")
        )
        process_source.delay(source.id)
        return source

    def ingest_file(self, user_id: int, title: str, file: UploadFile) -> KnowledgeSource:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        data = file.file.read()
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        source = self.repo.create(
            KnowledgeSource(user_id=user_id, title=title, source_type="pdf", content=text, status="queued")
        )
        process_source.delay(source.id)
        return source

    def remove_source(self, user_id: int, source_id: int) -> bool:
        source = self.repo.get_by_id(source_id)
        if not source or source.user_id != user_id:
            raise HTTPException(status_code=404, detail="Source not found")
        get_vector_store().delete_by_source(user_id=user_id, source_id=source_id)
        self.repo.delete(source)
        return True
