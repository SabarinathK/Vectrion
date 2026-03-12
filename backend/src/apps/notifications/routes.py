from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.apps.notifications.schemas import NotificationOut
from src.apps.notifications.services import NotificationService
from src.common.deps import get_current_user, get_db

router = APIRouter()


@router.get("", response_model=list[NotificationOut])
def list_notifications(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return NotificationService(db).list(user.id)


@router.delete("/clear")
def clear_notifications(user=Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = NotificationService(db).clear(user.id)
    return {"deleted": deleted}
