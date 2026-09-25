import abc
import uuid
from datetime import datetime
from typing import Dict, Any, List


class PredictionMonitoringRepository(metaclass=abc.ABCMeta):
    """Abstract interface for aggregating prediction_runs metrics."""

    @abc.abstractmethod
    async def get_aggregation_metrics(
        self, project_id: uuid.UUID, start: datetime, end: datetime
    ) -> Dict[str, Any]:
        """Calculates prediction totals, latency averages, failure counts, and cache rate percentages."""
        pass

    @abc.abstractmethod
    async def get_latency_trends(
        self, project_id: uuid.UUID, start: datetime, end: datetime, interval_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Retrieves timeseries aggregates of latencies and errors counts."""
        pass
