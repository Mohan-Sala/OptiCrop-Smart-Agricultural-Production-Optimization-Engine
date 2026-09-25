import uuid
from typing import Optional
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class Project(AppDocument):
    user_id: uuid.UUID
    name: str
    description: Optional[str] = None

    class Settings:
        name = "projects"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("name", ASCENDING)]),
        ]
