from typing import Any, List
from app.models.training_experiment import TrainingExperiment
from app.repositories.interfaces.experiment import ExperimentRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoExperimentRepository(MongoBaseRepository[TrainingExperiment], ExperimentRepository):
    """Concrete MongoDB / Beanie implementation of ExperimentRepository."""

    def __init__(self):
        super().__init__(TrainingExperiment)

    async def get_by_project_id(self, project_id: Any) -> List[TrainingExperiment]:
        parsed_project_id = to_uuid(project_id)
        return await TrainingExperiment.find(
            TrainingExperiment.project_id == parsed_project_id
        ).to_list()
