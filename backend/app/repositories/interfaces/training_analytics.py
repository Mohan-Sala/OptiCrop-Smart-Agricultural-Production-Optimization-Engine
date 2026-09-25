from abc import ABC, abstractmethod
from typing import Any, List, Dict


class TrainingAnalyticsRepository(ABC):
    """Abstract interface for aggregating training session execution history."""

    @abstractmethod
    async def get_session_statuses_count(self, project_id: Any) -> Dict[str, int]:
        """Returns session count distribution mapping completed, running, pending, failed runs."""
        pass

    @abstractmethod
    async def get_training_duration_metrics(self, project_id: Any) -> Dict[str, float]:
        """Returns average, min, max training execution times in seconds."""
        pass

    @abstractmethod
    async def get_experiments_summary(self, project_id: Any) -> List[Dict[str, Any]]:
        """Returns overview of experiments and their nested completed runs count."""
        pass
