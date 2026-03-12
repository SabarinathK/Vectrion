from sqlmodel import Session

from app.apps.notifications.models import Notification
from app.apps.notifications.repositories import NotificationRepository
from app.platform.events.pubsub import publish_event_sync


class NotificationService:
    def __init__(self, db: Session) -> None:
        self.repo = NotificationRepository(db)

    def create(self, user_id: int, title: str, message: str) -> Notification:
        notification = self.repo.create(Notification(user_id=user_id, title=title, message=message))
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
        return self.repo.list_by_user(user_id)

    def clear(self, user_id: int) -> int:
        count = self.repo.clear_by_user(user_id)
        publish_event_sync({"type": "notifications_cleared", "user_id": user_id})
        return count
