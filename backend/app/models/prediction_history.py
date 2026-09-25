import uuid
from typing import Dict, Any
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class PredictionHistory(AppDocument):
    user_id: uuid.UUID
    trained_model_id: uuid.UUID
    trained_model_version: str
    input_data: Dict[str, Any]
    prediction: str
    confidence: float

    class Settings:
        name = "prediction_histories"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("trained_model_id", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)]),
        ]
