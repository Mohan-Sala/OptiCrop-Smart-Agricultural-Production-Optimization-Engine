import abc
import uuid
from datetime import datetime
from typing import List, Optional
from app.models.external_telemetry import ExternalTelemetryLog
from app.repositories.interfaces.base import BaseRepository


class TelemetryRepository(BaseRepository[ExternalTelemetryLog], metaclass=abc.ABCMeta):
    """Abstract interface for storing and retrieving external telemetry ingestion data logs."""

    @abc.abstractmethod
    async def list_by_project_and_range(
        self, project_id: uuid.UUID, start: datetime, end: datetime
    ) -> List[ExternalTelemetryLog]:
        pass

    @abc.abstractmethod
    async def prune_telemetry(self, before: datetime) -> int:
        pass
