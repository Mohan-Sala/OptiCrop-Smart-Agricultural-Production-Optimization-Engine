from abc import abstractmethod
from typing import Any, List, Optional
from app.models.dataset_preprocessing import DatasetPreprocessing
from app.repositories.interfaces.base import BaseRepository


class PreprocessingRepository(BaseRepository[DatasetPreprocessing]):
    """Abstract interface for Preprocessing history-related database operations."""

    @abstractmethod
    async def get_by_dataset_id(self, dataset_id: Any) -> List[DatasetPreprocessing]:
        """Retrieves all preprocessing runs triggered on a specific dataset."""
        pass

    @abstractmethod
    async def get_by_hash_and_user(self, config_hash: str, user_id: Any) -> Optional[DatasetPreprocessing]:
        """Checks for an existing duplicate completed run config to enable reuse."""
        pass
