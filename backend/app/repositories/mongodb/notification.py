from typing import Any, List
from app.models.notification import Notification
from app.repositories.interfaces.notification import NotificationRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoNotificationRepository(MongoBaseRepository[Notification], NotificationRepository):
    """Concrete MongoDB / Beanie implementation of NotificationRepository."""

    def __init__(self):
        super().__init__(Notification)

    async def get_unread_by_user_id(self, user_id: Any) -> List[Notification]:
        parsed_user_id = to_uuid(user_id)
        return await Notification.find(
            Notification.user_id == parsed_user_id,
            Notification.is_read == False,
        ).sort("-created_at").to_list()

    async def mark_all_as_read(self, user_id: Any) -> bool:
        parsed_user_id = to_uuid(user_id)
        result = await Notification.find(
            Notification.user_id == parsed_user_id,
            Notification.is_read == False,
        ).update({"$set": {"is_read": True}})
        return result.modified_count > 0
