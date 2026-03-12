from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.apps.notifications.actions import clear_notifications_action, list_notifications_action
from app.apps.notifications.schemas import NotificationOut
from app.common.deps import get_current_user, get_db

router = APIRouter()


@router.get("", response_model=list[NotificationOut])
def list_notifications(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return list_notifications_action(db, user.id)


@router.delete("/clear")
def clear_notifications(user=Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = clear_notifications_action(db, user.id)
    return {"deleted": deleted}
