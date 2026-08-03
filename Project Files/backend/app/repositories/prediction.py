from abc import abstractmethod
from typing import List
from app.models.prediction_history import PredictionHistory
from app.repositories.base import BaseRepository


class PredictionRepository(BaseRepository[PredictionHistory]):
    """Abstract interface for PredictionHistory-related database operations."""

    @abstractmethod
    async def get_by_user_id(self, user_id: Any) -> List[PredictionHistory]:
        """Retrieves prediction logs created by a specific user."""
        pass

    @abstractmethod
    async def get_by_model_id(self, model_id: Any) -> List[PredictionHistory]:
        """Retrieves prediction execution history run on a specific model."""
        pass
