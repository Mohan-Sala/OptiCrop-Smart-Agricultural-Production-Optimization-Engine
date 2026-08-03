from abc import abstractmethod
from typing import List
from app.models.dataset import Dataset
from app.repositories.base import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
    """Abstract interface for Dataset-related database operations."""

    @abstractmethod
    async def get_by_project_id(self, project_id: Any) -> List[Dataset]:
        """Retrieves all datasets uploaded within a specific project."""
        pass
