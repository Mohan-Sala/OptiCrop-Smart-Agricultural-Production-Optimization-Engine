import uuid
from datetime import datetime
from typing import List
from app.models.external_telemetry import ExternalTelemetryLog
from app.repositories.interfaces.telemetry import TelemetryRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoTelemetryRepository(MongoBaseRepository[ExternalTelemetryLog], TelemetryRepository):
    """Concrete MongoDB / Beanie implementation of TelemetryRepository."""

    def __init__(self):
        super().__init__(ExternalTelemetryLog)

    async def list_by_project_and_range(
        self, project_id: uuid.UUID, start: datetime, end: datetime
    ) -> List[ExternalTelemetryLog]:
        parsed_project_id = to_uuid(project_id)
        return await ExternalTelemetryLog.find({
            "project_id": parsed_project_id,
            "recorded_at": {"$gte": start, "$lte": end},
        }).sort("+recorded_at").to_list()

    async def prune_telemetry(self, before: datetime) -> int:
        result = await ExternalTelemetryLog.find(
            ExternalTelemetryLog.recorded_at < before
        ).delete()
        return result.deleted_count
