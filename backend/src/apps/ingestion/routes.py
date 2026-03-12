from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlmodel import Session

from src.apps.ingestion.schemas import IngestTextRequest, IngestUrlRequest, SourceOut
from src.apps.ingestion.services import IngestionService
from src.common.deps import get_current_user, get_db

router = APIRouter()


@router.get("/sources", response_model=list[SourceOut])
def list_sources(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return IngestionService(db).list_sources(user.id)


@router.post("/ingest/text", response_model=SourceOut)
def ingest_text(payload: IngestTextRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return IngestionService(db).ingest_text(user.id, payload.title, payload.text)


@router.post("/ingest/url", response_model=SourceOut)
def ingest_url(payload: IngestUrlRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return IngestionService(db).ingest_url(user.id, payload.title, payload.url)


@router.post("/ingest/file", response_model=SourceOut)
def ingest_file(
    title: str = Form(...),
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return IngestionService(db).ingest_file(user.id, title, file)


@router.delete("/sources/{source_id}")
def remove_source(source_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    removed = IngestionService(db).remove_source(user.id, source_id)
    return {"removed": removed}
