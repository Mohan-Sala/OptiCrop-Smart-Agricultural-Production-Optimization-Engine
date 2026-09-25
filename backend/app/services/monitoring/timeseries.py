import uuid
from datetime import datetime
from typing import List, Dict, Any
from app.repositories.interfaces.prediction_monitoring import PredictionMonitoringRepository


class TimeSeriesAggregationService:
    """Combines prediction rates, latency histories, and caching hits into timeseries metrics."""

    def __init__(self, metrics_repo: PredictionMonitoringRepository):
        self.metrics_repo = metrics_repo

    async def get_trends(
        self, project_id: uuid.UUID, start: datetime, end: datetime, interval_hours: int = 24
    ) -> List[Dict[str, Any]]:
        return await self.metrics_repo.get_latency_trends(project_id, start, end, interval_hours)
