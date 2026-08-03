from abc import abstractmethod
from typing import Any, List, Optional
from app.models.trained_model import TrainedModel
from app.repositories.interfaces.base import BaseRepository


class TrainedModelRepository(BaseRepository[TrainedModel]):
    """Abstract interface for TrainedModel registry operations."""

    @abstractmethod
    async def get_by_project_id(self, project_id: Any) -> List[TrainedModel]:
        """Retrieves all registered models for a project."""
        pass

    @abstractmethod
    async def get_active_model(self, project_id: Any) -> Optional[TrainedModel]:
        """Retrieves the active model for a project."""
        pass

    @abstractmethod
    async def deactivate_all_in_project(self, project_id: Any) -> None:
        """Deactivates all models belonging to a project within the same transaction."""
        pass
