import uuid
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class UserSetting(AppDocument):
    user_id: uuid.UUID
    theme: str = "system"
    language: str = "en"
    notification_enabled: bool = True

    class Settings:
        name = "user_settings"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
        ]
