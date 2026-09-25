from abc import ABC, abstractmethod
from typing import Any, List, Dict


class ModelAnalyticsRepository(ABC):
    """Abstract interface for querying registered model registry metrics."""

    @abstractmethod
    async def get_lifecycle_status_distribution(self, project_id: Any) -> Dict[str, int]:
        """Returns distribution of model states (READY, TRAINING, FAILED, ARCHIVED, DEPRECATED)."""
        pass

    @abstractmethod
    async def get_registry_general_statistics(self, project_id: Any) -> Dict[str, Any]:
        """Returns average metrics (Accuracy, R2) of all ready models registered in a project."""
        pass
