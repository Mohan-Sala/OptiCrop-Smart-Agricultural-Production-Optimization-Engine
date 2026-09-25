from abc import abstractmethod
from typing import Any, List
from app.models.feature_metadata import FeatureMetadata
from app.repositories.interfaces.base import BaseRepository


class FeatureMetadataRepository(BaseRepository[FeatureMetadata]):
    """Abstract interface for FeatureMetadata catalog-related database operations."""

    @abstractmethod
    async def get_by_dataset_id(self, dataset_id: Any) -> List[FeatureMetadata]:
        """Retrieves all feature metadata catalog mappings for a dataset version."""
        pass

    @abstractmethod
    async def create_features_batch(self, features: List[FeatureMetadata]) -> List[FeatureMetadata]:
        """Bulk inserts a collection of feature metadata rows."""
        pass
