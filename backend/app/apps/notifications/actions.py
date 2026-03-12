from sqlmodel import Session

from app.apps.notifications.services import NotificationService


def list_notifications_action(db: Session, user_id: int):
    return NotificationService(db).list(user_id=user_id)


def clear_notifications_action(db: Session, user_id: int) -> int:
    return NotificationService(db).clear(user_id=user_id)
