import uuid
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class AlertRule(AppDocument):
    project_id: uuid.UUID
    metric_name: str
    threshold_value: float
    comparison_operator: str
    is_active: bool = True

    class Settings:
        name = "alert_rules"
        indexes = [
            IndexModel([("project_id", ASCENDING)]),
            IndexModel([("project_id", ASCENDING), ("is_active", ASCENDING)]),
        ]
