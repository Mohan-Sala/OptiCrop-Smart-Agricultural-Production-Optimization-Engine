import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument
from app.core.enums import DriftStatus


class DriftSnapshot(AppDocument):
    project_id: uuid.UUID
    model_id: uuid.UUID
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    method_name: str
    drift_score: float
    is_drifted: bool = False
    feature_drifts: Dict[str, Any]
    target_drift: Optional[Dict[str, Any]] = None

    baseline_statistics_version: str
    algorithm_version: str
    status: DriftStatus = DriftStatus.PENDING
    error_message: Optional[str] = None

    class Settings:
        name = "drift_snapshots"
        indexes = [
            IndexModel([("project_id", ASCENDING)]),
            IndexModel([("model_id", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("computed_at", ASCENDING)]),
        ]
