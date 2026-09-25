import uuid
from typing import Dict, Any
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class HyperparameterSet(AppDocument):
    trained_model_id: uuid.UUID
    parameters: Dict[str, Any]

    class Settings:
        name = "hyperparameter_sets"
        indexes = [
            IndexModel([("trained_model_id", ASCENDING)]),
        ]
