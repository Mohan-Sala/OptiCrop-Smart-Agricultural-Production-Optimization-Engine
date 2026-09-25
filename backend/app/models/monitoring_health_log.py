from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class MonitoringHealthLog(AppDocument):
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    database_healthy: bool
    storage_healthy: bool
    cache_healthy: bool
    worker_healthy: bool
    response_latency_ms: float
    details: Optional[Dict[str, Any]] = None

    class Settings:
        name = "monitoring_health_logs"
        indexes = [
            IndexModel([("recorded_at", ASCENDING)]),
        ]
