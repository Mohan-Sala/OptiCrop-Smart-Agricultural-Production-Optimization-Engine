from abc import ABC, abstractmethod
from typing import Any, List
from app.models.prediction_run import PredictionRun


class PredictionAuditRepository(ABC):
    """Abstract interface for system performance monitoring audits of predictions."""

    @abstractmethod
    async def get_system_audit_metrics(self, project_id: Any) -> List[PredictionRun]:
        """Retrieves prediction runs with full timing metrics for performance dashboard metrics."""
        pass
