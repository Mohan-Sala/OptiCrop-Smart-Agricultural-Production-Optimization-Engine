from typing import Any, Dict
from app.models.dataset import Dataset
from app.models.dataset_preprocessing import DatasetPreprocessing
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.repositories.interfaces.project_analytics import ProjectAnalyticsRepository
from app.repositories.mongodb.base import to_uuid


class MongoProjectAnalyticsRepository(ProjectAnalyticsRepository):
    """Concrete MongoDB / Beanie implementation of ProjectAnalyticsRepository."""

    def __init__(self):
        pass

    async def get_overview_counts(self, project_id: Any) -> Dict[str, Any]:
        parsed_project_id = to_uuid(project_id)
        
        # Count datasets
        datasets = await Dataset.find(
            Dataset.project_id == parsed_project_id,
            Dataset.is_deleted == False,
        ).to_list()
        datasets_count = len(datasets)
        dataset_ids = [d.id for d in datasets]

        # Count preprocessing runs
        prep_count = await DatasetPreprocessing.find(
            DatasetPreprocessing.project_id == parsed_project_id
        ).count()

        # Count training runs
        if dataset_ids:
            training_count = await TrainingSession.find({
                "dataset_id": {"$in": dataset_ids}
            }).count()
            sessions = await TrainingSession.find({
                "dataset_id": {"$in": dataset_ids}
            }).to_list()
            session_ids = [s.id for s in sessions]
            models_count = await TrainedModel.find({
                "training_session_id": {"$in": session_ids}
            }).count() if session_ids else 0
        else:
            training_count = 0
            models_count = 0

        return {
            "datasets_count": datasets_count,
            "preprocessing_runs_count": prep_count,
            "training_sessions_count": training_count,
            "registered_models_count": models_count,
        }

    async def get_storage_usage(self, project_id: Any) -> int:
        parsed_project_id = to_uuid(project_id)
        datasets = await Dataset.find(
            Dataset.project_id == parsed_project_id,
            Dataset.is_deleted == False,
        ).to_list()
        return sum(d.size for d in datasets)
