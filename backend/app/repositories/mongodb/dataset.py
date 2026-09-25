import re
from typing import Any, List, Optional, Tuple
from app.models.dataset import Dataset
from app.models.dataset_statistics import DatasetStatistics, DatasetStatisticsEmbedded
from app.models.feature_metadata import FeatureMetadata
from app.core.enums import DatasetStatus, DatasetStage
from app.repositories.interfaces.dataset import DatasetRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoDatasetRepository(MongoBaseRepository[Dataset], DatasetRepository):
    """Concrete MongoDB / Beanie implementation of DatasetRepository."""

    def __init__(self, *args, **kwargs):
        super().__init__(Dataset, *args, **kwargs)

    async def _populate_relations(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        if not dataset:
            return None
        # Populate statistics if not already present
        if dataset.statistics is None:
            stats = await DatasetStatistics.find_one(DatasetStatistics.dataset_id == dataset.id)
            if stats:
                dataset.statistics = stats
        # Populate feature catalog
        features = await FeatureMetadata.find(FeatureMetadata.dataset_id == dataset.id).to_list()
        dataset.feature_catalog = features
        return dataset

    async def get_by_id(self, id: Any) -> Optional[Dataset]:
        parsed_id = to_uuid(id)
        dataset = await Dataset.get(parsed_id)
        if not dataset and parsed_id != id:
            dataset = await Dataset.get(id)
        return await self._populate_relations(dataset)

    async def get_by_project_id(self, project_id: Any) -> List[Dataset]:
        parsed_project_id = to_uuid(project_id)
        datasets = await Dataset.find(
            Dataset.project_id == parsed_project_id,
            Dataset.is_deleted == False,
        ).to_list()
        for d in datasets:
            await self._populate_relations(d)
        return datasets

    async def get_by_id_and_user_id(self, dataset_id: Any, user_id: Any) -> Optional[Dataset]:
        parsed_dataset_id = to_uuid(dataset_id)
        parsed_user_id = to_uuid(user_id)
        dataset = await Dataset.find_one(
            Dataset.id == parsed_dataset_id,
            Dataset.user_id == parsed_user_id,
            Dataset.is_deleted == False,
        )
        return await self._populate_relations(dataset)

    async def get_by_sha256_and_user(self, sha256: str, user_id: Any) -> Optional[Dataset]:
        parsed_user_id = to_uuid(user_id)
        dataset = await Dataset.find_one(
            Dataset.sha256_checksum == sha256,
            Dataset.user_id == parsed_user_id,
            Dataset.is_deleted == False,
        )
        return await self._populate_relations(dataset)

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
        parsed_user_id = to_uuid(user_id)
        query: dict = {
            "user_id": parsed_user_id,
            "is_deleted": False,
        }

        if project_id is not None:
            query["project_id"] = to_uuid(project_id)
        if stage is not None:
            query["dataset_stage"] = stage
        if status is not None:
            query["status"] = status
        if is_latest is not None:
            query["is_latest"] = is_latest
        if search:
            escaped = re.escape(search)
            regex = {"$regex": escaped, "$options": "i"}
            query["$or"] = [
                {"name": regex},
                {"description": regex},
                {"original_filename": regex},
            ]

        cursor = Dataset.find(query)
        total_count = await cursor.count()

        sort_dir = "-" if sort_desc else "+"
        cursor = cursor.sort(f"{sort_dir}{sort_by}")

        offset_val = (page - 1) * page_size
        datasets = await cursor.skip(offset_val).limit(page_size).to_list()

        for d in datasets:
            await self._populate_relations(d)

        return datasets, total_count
