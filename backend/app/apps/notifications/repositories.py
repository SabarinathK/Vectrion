from sqlmodel import Session, delete, select

from app.apps.notifications.models import Notification


class NotificationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def list_by_user(self, user_id: int) -> list[Notification]:
        return list(
            self.db.exec(
                select(Notification)
                .where(Notification.user_id == user_id)
                .order_by(Notification.created_at.desc())
            ).all()
        )

    def clear_by_user(self, user_id: int) -> int:
        result = self.db.exec(delete(Notification).where(Notification.user_id == user_id))
        self.db.commit()
        return int(result.rowcount or 0)
