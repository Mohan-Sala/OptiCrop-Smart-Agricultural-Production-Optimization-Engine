from abc import ABC, abstractmethod
from typing import Any, Dict


class ProjectAnalyticsRepository(ABC):
    """Abstract interface for aggregating project-wide analytics."""

    @abstractmethod
    async def get_overview_counts(self, project_id: Any) -> Dict[str, Any]:
        """Returns aggregates count of datasets, preprocessing runs, training runs, models."""
        pass

    @abstractmethod
    async def get_storage_usage(self, project_id: Any) -> int:
        """Returns sum of bytes of all datasets stored under this project."""
        pass
