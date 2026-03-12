from celery import Celery
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlmodel import Session

from app.apps.ingestion.models import KnowledgeChunk
from app.apps.ingestion.repositories import ChunkRepository, SourceRepository
from app.apps.notifications.services import NotificationService
from app.common.config import get_settings
from app.platform.db.models import *  # noqa: F403,F401
from app.platform.db.session import engine
from app.platform.events.pubsub import publish_event_sync
from app.platform.vectorstore.chroma_store import get_vector_store

settings = get_settings()
celery_app = Celery("rag_worker", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name="process_source")
def process_source(source_id: int) -> None:
    with Session(engine) as db:
        source_repo = SourceRepository(db)
        chunk_repo = ChunkRepository(db)
        notifier = NotificationService(db)

        source = source_repo.get_by_id(source_id)
        if not source:
            return

        try:
            source.status = "processing"
            source_repo.update(source)
            publish_event_sync(
                {
                    "type": "source_updated",
                    "user_id": source.user_id,
                    "source": {"id": source.id, "status": source.status},
                }
            )

            splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
            chunks = splitter.split_text(source.content or "")

            chunk_rows = [
                KnowledgeChunk(source_id=source.id, user_id=source.user_id, chunk_index=i, text=text)
                for i, text in enumerate(chunks)
                if text.strip()
            ]
            if chunk_rows:
                chunk_repo.bulk_create(chunk_rows)
                get_vector_store().add_chunks(source.user_id, source.id, [c.text for c in chunk_rows])

            source.status = "done"
            source_repo.update(source)
            notifier.create(source.user_id, "Ingestion Complete", f"{source.title} is ready for Q&A")
            publish_event_sync(
                {
                    "type": "source_updated",
                    "user_id": source.user_id,
                    "source": {"id": source.id, "status": source.status},
                }
            )
        except Exception as exc:
            db.rollback()
            source = source_repo.get_by_id(source_id)
            if source:
                source.status = "failed"
                source_repo.update(source)
                notifier.create(source.user_id, "Ingestion Failed", str(exc))
                publish_event_sync(
                    {
                        "type": "source_updated",
                        "user_id": source.user_id,
                        "source": {"id": source.id, "status": source.status},
                    }
                )
            raise
