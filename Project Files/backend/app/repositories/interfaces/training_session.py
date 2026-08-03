from abc import abstractmethod
from typing import Any, List, Optional
from app.models.training_session import TrainingSession
from app.repositories.interfaces.base import BaseRepository


class TrainingSessionRepository(BaseRepository[TrainingSession]):
    """Abstract interface for TrainingSession database operations."""

    @abstractmethod
    async def get_by_project_id(self, project_id: Any) -> List[TrainingSession]:
        """Retrieves all training sessions inside a project."""
        pass

    @abstractmethod
    async def get_by_hash_and_user(self, config_hash: str, user_id: Any) -> Optional[TrainingSession]:
        """Checks for duplicate completed training config run to allow caching."""
        pass
