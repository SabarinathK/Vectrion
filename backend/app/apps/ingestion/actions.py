from fastapi import UploadFile
from sqlmodel import Session

from app.apps.ingestion.services import IngestionService


def list_sources_action(db: Session, user_id: int):
    return IngestionService(db).list_sources(user_id=user_id)


def ingest_text_action(db: Session, user_id: int, title: str, text: str):
    return IngestionService(db).ingest_text(user_id=user_id, title=title, text=text)


def ingest_url_action(db: Session, user_id: int, title: str, url: str):
    return IngestionService(db).ingest_url(user_id=user_id, title=title, url=url)


def ingest_file_action(db: Session, user_id: int, title: str, file: UploadFile):
    return IngestionService(db).ingest_file(user_id=user_id, title=title, file=file)


def remove_source_action(db: Session, user_id: int, source_id: int):
    return IngestionService(db).remove_source(user_id=user_id, source_id=source_id)
