import uuid
from typing import Optional
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class TrainingExperiment(AppDocument):
    project_id: uuid.UUID
    name: str
    description: Optional[str] = None

    class Settings:
        name = "training_experiments"
        indexes = [
            IndexModel([("project_id", ASCENDING)]),
            IndexModel([("project_id", ASCENDING), ("name", ASCENDING)]),
        ]
