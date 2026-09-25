import uuid
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class Notification(AppDocument):
    user_id: uuid.UUID
    title: str
    message: str
    type: str = "info"
    priority: str = "medium"
    is_read: bool = False

    class Settings:
        name = "notifications"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("is_read", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)]),
        ]
