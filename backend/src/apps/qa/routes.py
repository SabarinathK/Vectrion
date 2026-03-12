from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.apps.qa.schemas import AskRequest, AskResponse
from src.apps.qa.services import QAService
from src.common.deps import get_current_user, get_db

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    answer = QAService(db).ask(user.id, payload.question)
    return AskResponse(answer=answer)
