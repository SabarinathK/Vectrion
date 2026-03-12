from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.apps.qa.actions import ask_action
from app.apps.qa.schemas import AskRequest, AskResponse
from app.common.deps import get_current_user, get_db

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    answer = ask_action(db, user.id, payload.question)
    return AskResponse(answer=answer)
