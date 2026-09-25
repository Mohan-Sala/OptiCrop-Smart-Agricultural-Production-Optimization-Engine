from abc import abstractmethod
from typing import Any, List
from app.models.training_experiment import TrainingExperiment
from app.repositories.interfaces.base import BaseRepository


class ExperimentRepository(BaseRepository[TrainingExperiment]):
    """Abstract interface for TrainingExperiment database operations."""

    @abstractmethod
    async def get_by_project_id(self, project_id: Any) -> List[TrainingExperiment]:
        """Retrieves all experiments associated with a project."""
        pass
