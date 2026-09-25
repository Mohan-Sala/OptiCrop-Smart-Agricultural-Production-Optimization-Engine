from typing import Any, List, Optional
from app.models.dataset_preprocessing import DatasetPreprocessing
from app.models.preprocessing_artifact import PreprocessingArtifact
from app.repositories.interfaces.preprocessing import PreprocessingRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoPreprocessingRepository(MongoBaseRepository[DatasetPreprocessing], PreprocessingRepository):
    """Concrete MongoDB / Beanie implementation of PreprocessingRepository."""

    def __init__(self):
        super().__init__(DatasetPreprocessing)

    async def _populate_artifacts(self, run: Optional[DatasetPreprocessing]) -> Optional[DatasetPreprocessing]:
        if not run:
            return None
        artifacts = await PreprocessingArtifact.find(
            PreprocessingArtifact.preprocessing_run_id == run.id
        ).to_list()
        run.artifacts = artifacts
        return run

    async def get_by_id(self, id: Any) -> Optional[DatasetPreprocessing]:
        parsed_id = to_uuid(id)
        run = await DatasetPreprocessing.get(parsed_id)
        if not run and parsed_id != id:
            run = await DatasetPreprocessing.get(id)
        return await self._populate_artifacts(run)

    async def get_by_dataset_id(self, dataset_id: Any) -> List[DatasetPreprocessing]:
        parsed_dataset_id = to_uuid(dataset_id)
        runs = await DatasetPreprocessing.find(
            DatasetPreprocessing.dataset_id == parsed_dataset_id
        ).sort("-created_at").to_list()
        for r in runs:
            await self._populate_artifacts(r)
        return runs

    async def get_by_hash_and_user(self, config_hash: str, user_id: Any) -> Optional[DatasetPreprocessing]:
        parsed_user_id = to_uuid(user_id)
        run = await DatasetPreprocessing.find_one(
            DatasetPreprocessing.preprocessing_hash == config_hash,
            DatasetPreprocessing.user_id == parsed_user_id,
            DatasetPreprocessing.status == "COMPLETED",
        )
        return await self._populate_artifacts(run)
