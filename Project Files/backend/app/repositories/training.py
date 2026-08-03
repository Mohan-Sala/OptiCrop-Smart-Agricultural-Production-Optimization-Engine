from abc import abstractmethod
from typing import List, Optional
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.repositories.base import BaseRepository


class TrainingRepository(BaseRepository[TrainingSession]):
    """Abstract interface for TrainingSession-related database operations."""

    @abstractmethod
    async def get_by_dataset_id(self, dataset_id: Any) -> List[TrainingSession]:
        """Retrieves all training sessions running on a specific dataset."""
        pass

    @abstractmethod
    async def create_trained_model(self, model: TrainedModel) -> TrainedModel:
        """Saves a newly trained model record to persistence storage."""
        pass

    @abstractmethod
    async def get_trained_model_by_id(self, model_id: Any) -> Optional[TrainedModel]:
        """Retrieves a single trained model metadata by ID."""
        pass
