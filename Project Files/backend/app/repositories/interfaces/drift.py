import abc
import uuid
from datetime import datetime
from typing import List, Optional
from app.models.drift_snapshot import DriftSnapshot
from app.repositories.interfaces.base import BaseRepository


class DriftRepository(BaseRepository[DriftSnapshot], metaclass=abc.ABCMeta):
    """Abstract interface for storing and fetching model drift snapshots."""

    @abc.abstractmethod
    async def get_latest_by_model(self, model_id: uuid.UUID) -> Optional[DriftSnapshot]:
        pass

    @abc.abstractmethod
    async def list_snapshots_by_project(
        self, project_id: uuid.UUID, limit: int = 100
    ) -> List[DriftSnapshot]:
        pass

    @abc.abstractmethod
    async def prune_snapshots(self, before: datetime, exclude_active_model_ids: List[uuid.UUID]) -> int:
        pass
