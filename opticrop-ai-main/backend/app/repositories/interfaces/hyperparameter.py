from abc import abstractmethod
from typing import Any, Optional
from app.models.hyperparameter_set import HyperparameterSet
from app.repositories.interfaces.base import BaseRepository


class HyperparameterSetRepository(BaseRepository[HyperparameterSet]):
    """Abstract interface for HyperparameterSet database operations."""

    @abstractmethod
    async def get_by_model_id(self, model_id: Any) -> Optional[HyperparameterSet]:
        """Retrieves hyperparameters set for a trained model."""
        pass
