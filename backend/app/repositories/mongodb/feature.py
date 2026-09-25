from typing import Any, List
from app.models.feature_metadata import FeatureMetadata
from app.repositories.interfaces.feature import FeatureMetadataRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoFeatureMetadataRepository(MongoBaseRepository[FeatureMetadata], FeatureMetadataRepository):
    """Concrete MongoDB / Beanie implementation of FeatureMetadataRepository."""

    def __init__(self):
        super().__init__(FeatureMetadata)

    async def get_by_dataset_id(self, dataset_id: Any) -> List[FeatureMetadata]:
        parsed_dataset_id = to_uuid(dataset_id)
        return await FeatureMetadata.find(FeatureMetadata.dataset_id == parsed_dataset_id).to_list()

    async def create_features_batch(self, features: List[FeatureMetadata]) -> List[FeatureMetadata]:
        if features:
            await FeatureMetadata.insert_many(features)
        return features
