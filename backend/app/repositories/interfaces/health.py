import abc
from datetime import datetime
from typing import List, Optional
from app.models.monitoring_health_log import MonitoringHealthLog
from app.repositories.interfaces.base import BaseRepository


class HealthRepository(BaseRepository[MonitoringHealthLog], metaclass=abc.ABCMeta):
    """Abstract interface for health log history logs repository."""

    @abc.abstractmethod
    async def list_health_history(self, limit: int = 100) -> List[MonitoringHealthLog]:
        pass

    @abc.abstractmethod
    async def prune_health_logs(self, before: datetime) -> int:
        pass
