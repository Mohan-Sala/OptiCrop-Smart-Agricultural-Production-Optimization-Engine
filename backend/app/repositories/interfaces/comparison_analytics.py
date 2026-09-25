from abc import ABC, abstractmethod
from typing import Any, List
from app.models.trained_model import TrainedModel


class ComparisonAnalyticsRepository(ABC):
    """Abstract interface for extracting model and metric datasets for side-by-side comparison."""

    @abstractmethod
    async def get_models_by_ids(self, model_ids: List[Any]) -> List[TrainedModel]:
        """Eagerly retrieves trained models and evaluation reports mapping to a list of IDs."""
        pass
