from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlmodel import Session

from src.apps.ingestion.models import KnowledgeChunk
from src.apps.ingestion.services import IngestionService
from src.apps.notifications.services import NotificationService
from src.platform.db.models import *
from src.platform.db.session import engine
from src.platform.events.pubsub import publish_event_sync
from src.platform.messaging.celery_app import celery_app
from src.platform.vectorstore.chroma_store import get_vector_store


@celery_app.task(name="process_source")
def process_source(source_id: int) -> None:
    with Session(engine) as db:
        ingestion_service = IngestionService(db)
        notifier = NotificationService(db)

        source = ingestion_service.get_source_by_id(source_id)
        if not source:
            return

        try:
            source.status = "processing"
            ingestion_service.update_source(source)
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
                KnowledgeChunk(
                    source_id=source.id,
                    user_id=source.user_id,
                    chunk_index=i,
                    text=text,
                )
                for i, text in enumerate(chunks)
                if text.strip()
            ]
            if chunk_rows:
                ingestion_service.bulk_create_chunks(chunk_rows)
                get_vector_store().add_chunks(
                    source.user_id, source.id, [c.text for c in chunk_rows]
                )

            source.status = "done"
            ingestion_service.update_source(source)
            notifier.create(
                source.user_id, "Ingestion Complete", f"{source.title} is ready for Q&A"
            )
            publish_event_sync(
                {
                    "type": "source_updated",
                    "user_id": source.user_id,
                    "source": {"id": source.id, "status": source.status},
                }
            )
        except Exception as exc:
            db.rollback()
            source = ingestion_service.get_source_by_id(source_id)
            if source:
                source.status = "failed"
                ingestion_service.update_source(source)
                notifier.create(source.user_id, "Ingestion Failed", str(exc))
                publish_event_sync(
                    {
                        "type": "source_updated",
                        "user_id": source.user_id,
                        "source": {"id": source.id, "status": source.status},
                    }
                )
            raise
