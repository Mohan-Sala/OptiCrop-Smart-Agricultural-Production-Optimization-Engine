from abc import abstractmethod
from typing import Any, List
from app.models.preprocessing_artifact import PreprocessingArtifact
from app.repositories.interfaces.base import BaseRepository


class PreprocessingArtifactRepository(BaseRepository[PreprocessingArtifact]):
    """Abstract interface for PreprocessingArtifact-related database operations."""

    @abstractmethod
    async def get_by_run_id(self, run_id: Any) -> List[PreprocessingArtifact]:
        """Retrieves all serialized artifacts generated during a specific run."""
        pass
