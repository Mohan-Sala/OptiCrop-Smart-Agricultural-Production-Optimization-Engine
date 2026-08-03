import uuid
from datetime import datetime
from typing import Dict, Any
from app.repositories.interfaces.prediction_monitoring import PredictionMonitoringRepository


class PredictionMetricsService:
    """Manages latency averages, cache hits counts, queue diagnostics, and error statistics."""

    def __init__(self, metrics_repo: PredictionMonitoringRepository):
        self.metrics_repo = metrics_repo

    async def get_metrics(
        self, project_id: uuid.UUID, start: datetime, end: datetime
    ) -> Dict[str, Any]:
        return await self.metrics_repo.get_aggregation_metrics(project_id, start, end)
