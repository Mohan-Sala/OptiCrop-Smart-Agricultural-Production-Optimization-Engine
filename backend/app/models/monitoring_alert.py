import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument
from app.core.enums import AlertStatus


class MonitoringAlert(AppDocument):
    project_id: uuid.UUID
    model_id: uuid.UUID
    rule_id: Optional[uuid.UUID] = None
    rule_name: str
    severity: str
    message: str
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    status: AlertStatus = AlertStatus.ACTIVE

    occurrence_count: int = 1
    last_triggered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Lifecycle tracing
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[uuid.UUID] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[uuid.UUID] = None

    class Settings:
        name = "monitoring_alerts"
        indexes = [
            IndexModel([("project_id", ASCENDING)]),
            IndexModel([("model_id", ASCENDING)]),
            IndexModel([("rule_id", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("last_triggered_at", ASCENDING)]),
        ]
