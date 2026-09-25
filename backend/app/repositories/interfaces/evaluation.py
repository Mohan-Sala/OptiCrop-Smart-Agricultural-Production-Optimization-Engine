from abc import abstractmethod
from typing import Any, Optional
from app.models.evaluation_report import EvaluationReport
from app.repositories.interfaces.base import BaseRepository


class EvaluationReportRepository(BaseRepository[EvaluationReport]):
    """Abstract interface for EvaluationReport database operations."""

    @abstractmethod
    async def get_by_model_id(self, model_id: Any) -> Optional[EvaluationReport]:
        """Retrieves evaluation report for a trained model."""
        pass
