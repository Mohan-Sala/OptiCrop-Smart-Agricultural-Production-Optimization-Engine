from abc import abstractmethod
from typing import Any, List, Optional, Tuple
from app.models.dataset import Dataset
from app.repositories.interfaces.base import BaseRepository
from app.core.enums import DatasetStatus, DatasetStage


class DatasetRepository(BaseRepository[Dataset]):
    """Abstract interface for Dataset-related database operations."""

    @abstractmethod
    async def get_by_project_id(self, project_id: Any) -> List[Dataset]:
        """Retrieves all datasets uploaded within a specific project."""
        pass

    @abstractmethod
    async def get_by_id_and_user_id(self, dataset_id: Any, user_id: Any) -> Optional[Dataset]:
        """Retrieves a specific dataset by ID if it belongs to the user and is not deleted."""
        pass

    @abstractmethod
    async def list_datasets_paginated(
        self,
        user_id: Any,
        project_id: Optional[Any] = None,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        stage: Optional[DatasetStage] = None,
        status: Optional[DatasetStatus] = None,
        is_latest: Optional[bool] = None,
        sort_by: str = "uploaded_at",
        sort_desc: bool = True,
    ) -> Tuple[List[Dataset], int]:
        """Lists active (non-soft-deleted) datasets with search, filters, pagination, and sorting."""
        pass

    @abstractmethod
    async def get_by_sha256_and_user(self, sha256: str, user_id: Any) -> Optional[Dataset]:
        """Checks for existing duplicate active dataset by sha256 checksum for the user."""
        pass
