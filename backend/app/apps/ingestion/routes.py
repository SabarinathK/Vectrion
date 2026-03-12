from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlmodel import Session

from app.apps.ingestion.actions import (
    ingest_file_action,
    ingest_text_action,
    ingest_url_action,
    list_sources_action,
    remove_source_action,
)
from app.apps.ingestion.schemas import IngestTextRequest, IngestUrlRequest, SourceOut
from app.common.deps import get_current_user, get_db

router = APIRouter()


@router.get("/sources", response_model=list[SourceOut])
def list_sources(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return list_sources_action(db, user.id)


@router.post("/ingest/text", response_model=SourceOut)
def ingest_text(payload: IngestTextRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return ingest_text_action(db, user.id, payload.title, payload.text)


@router.post("/ingest/url", response_model=SourceOut)
def ingest_url(payload: IngestUrlRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return ingest_url_action(db, user.id, payload.title, payload.url)


@router.post("/ingest/file", response_model=SourceOut)
def ingest_file(
    title: str = Form(...),
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ingest_file_action(db, user.id, title, file)


@router.delete("/sources/{source_id}")
def remove_source(source_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    removed = remove_source_action(db, user.id, source_id)
    return {"removed": removed}
