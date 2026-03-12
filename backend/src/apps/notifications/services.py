from sqlmodel import Session, delete, select

from src.apps.notifications.models import Notification
from src.platform.events.pubsub import publish_event_sync


class NotificationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_notification(self, notification: Notification) -> Notification:
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

    def create(self, user_id: int, title: str, message: str) -> Notification:
        notification = self.create_notification(Notification(user_id=user_id, title=title, message=message))
        publish_event_sync(
            {
                "type": "notification_created",
                "user_id": user_id,
                "notification": {
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "created_at": notification.created_at.isoformat(),
                },
            }
        )
        return notification

    def list(self, user_id: int):
        return self.list_by_user(user_id)

    def clear(self, user_id: int) -> int:
        count = self.clear_by_user(user_id)
        publish_event_sync({"type": "notifications_cleared", "user_id": user_id})
        return count
