import uuid
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class ModelMetric(AppDocument):
    trained_model_id: uuid.UUID
    metric_name: str
    metric_value: float

    class Settings:
        name = "model_metrics"
        indexes = [
            IndexModel([("trained_model_id", ASCENDING)]),
            IndexModel([("trained_model_id", ASCENDING), ("metric_name", ASCENDING)]),
        ]
