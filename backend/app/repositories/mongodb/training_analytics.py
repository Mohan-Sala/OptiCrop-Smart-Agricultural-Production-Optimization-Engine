from typing import Any, List, Dict
from app.models.dataset import Dataset
from app.models.training_session import TrainingSession
from app.models.training_experiment import TrainingExperiment
from app.repositories.interfaces.training_analytics import TrainingAnalyticsRepository
from app.repositories.mongodb.base import to_uuid


class MongoTrainingAnalyticsRepository(TrainingAnalyticsRepository):
    """Concrete MongoDB / Beanie implementation of TrainingAnalyticsRepository."""

    def __init__(self):
        pass

    async def _get_project_dataset_ids(self, project_id: Any) -> List[Any]:
        parsed_project_id = to_uuid(project_id)
        datasets = await Dataset.find(
            Dataset.project_id == parsed_project_id,
            Dataset.is_deleted == False,
        ).to_list()
        return [d.id for d in datasets]

    async def get_session_statuses_count(self, project_id: Any) -> Dict[str, int]:
        dataset_ids = await self._get_project_dataset_ids(project_id)
        counts = {"PENDING": 0, "TRAINING": 0, "COMPLETED": 0, "FAILED": 0}
        if not dataset_ids:
            return counts
        sessions = await TrainingSession.find({"dataset_id": {"$in": dataset_ids}}).to_list()
        for s in sessions:
            st = s.status.upper() if s.status else "PENDING"
            counts[st] = counts.get(st, 0) + 1
        return counts

    async def get_training_duration_metrics(self, project_id: Any) -> Dict[str, float]:
        dataset_ids = await self._get_project_dataset_ids(project_id)
        if not dataset_ids:
            return {"average_time": 0.0, "minimum_time": 0.0, "maximum_time": 0.0}
        sessions = await TrainingSession.find({
            "dataset_id": {"$in": dataset_ids},
            "status": "COMPLETED",
        }).to_list()
        times = [s.training_time for s in sessions if s.training_time is not None]
        if not times:
            return {"average_time": 0.0, "minimum_time": 0.0, "maximum_time": 0.0}
        return {
            "average_time": float(sum(times) / len(times)),
            "minimum_time": float(min(times)),
            "maximum_time": float(max(times)),
        }

    async def get_experiments_summary(self, project_id: Any) -> List[Dict[str, Any]]:
        parsed_project_id = to_uuid(project_id)
        experiments = await TrainingExperiment.find(
            TrainingExperiment.project_id == parsed_project_id
        ).to_list()
        summary = []
        for exp in experiments:
            count = await TrainingSession.find(TrainingSession.experiment_id == exp.id).count()
            summary.append({
                "experiment_id": str(exp.id),
                "name": exp.name,
                "description": exp.description,
                "sessions_count": count,
            })
        return summary
