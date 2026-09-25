import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class ExternalTelemetryLog(AppDocument):
    project_id: uuid.UUID
    provider_name: str
    source_id: Optional[str] = None
    provider_record_id: Optional[str] = None
    ingestion_status: str = "VALIDATED"
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    normalized_payload: Dict[str, Any]

    class Settings:
        name = "external_telemetry_logs"
        indexes = [
            IndexModel([("project_id", ASCENDING)]),
            IndexModel([("recorded_at", ASCENDING)]),
            IndexModel([("provider_name", ASCENDING)]),
        ]
