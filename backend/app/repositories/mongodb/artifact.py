from typing import Any, List
from app.models.preprocessing_artifact import PreprocessingArtifact
from app.repositories.interfaces.artifact import PreprocessingArtifactRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoPreprocessingArtifactRepository(
    MongoBaseRepository[PreprocessingArtifact], PreprocessingArtifactRepository
):
    """Concrete MongoDB / Beanie implementation of PreprocessingArtifactRepository."""

    def __init__(self):
        super().__init__(PreprocessingArtifact)

    async def get_by_run_id(self, run_id: Any) -> List[PreprocessingArtifact]:
        parsed_run_id = to_uuid(run_id)
        return await PreprocessingArtifact.find(
            PreprocessingArtifact.preprocessing_run_id == parsed_run_id
        ).to_list()
