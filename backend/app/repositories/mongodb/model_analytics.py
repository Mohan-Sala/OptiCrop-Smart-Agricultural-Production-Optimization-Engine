from typing import Any, Dict
from app.models.dataset import Dataset
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.models.model_metric import ModelMetric
from app.repositories.interfaces.model_analytics import ModelAnalyticsRepository
from app.repositories.mongodb.base import to_uuid


class MongoModelAnalyticsRepository(ModelAnalyticsRepository):
    """Concrete MongoDB / Beanie implementation of ModelAnalyticsRepository."""

    def __init__(self):
        pass

    async def _get_project_model_ids(self, project_id: Any) -> tuple[list[Any], list[TrainedModel]]:
        parsed_project_id = to_uuid(project_id)
        datasets = await Dataset.find(
            Dataset.project_id == parsed_project_id,
            Dataset.is_deleted == False,
        ).to_list()
        dataset_ids = [d.id for d in datasets]
        if not dataset_ids:
            return [], []
        sessions = await TrainingSession.find({"dataset_id": {"$in": dataset_ids}}).to_list()
        session_ids = [s.id for s in sessions]
        if not session_ids:
            return [], []
        models = await TrainedModel.find({"training_session_id": {"$in": session_ids}}).to_list()
        return [m.id for m in models], models

    async def get_lifecycle_status_distribution(self, project_id: Any) -> Dict[str, int]:
        _, models = await self._get_project_model_ids(project_id)
        dist = {"READY": 0, "TRAINING": 0, "FAILED": 0, "ARCHIVED": 0, "DEPRECATED": 0}
        for m in models:
            st = m.status.upper() if m.status else "READY"
            dist[st] = dist.get(st, 0) + 1
        return dist

    async def get_registry_general_statistics(self, project_id: Any) -> Dict[str, Any]:
        model_ids, models = await self._get_project_model_ids(project_id)
        metrics_averages: Dict[str, float] = {}

        if model_ids:
            ready_model_ids = [m.id for m in models if m.status == "READY"]
            if ready_model_ids:
                metrics = await ModelMetric.find({"trained_model_id": {"$in": ready_model_ids}}).to_list()
                metric_groups: Dict[str, list[float]] = {}
                for met in metrics:
                    metric_groups.setdefault(met.metric_name, []).append(met.metric_value)
                for name, values in metric_groups.items():
                    metrics_averages[name] = float(sum(values) / len(values))

        active_model_info = None
        active_model = next((m for m in models if m.is_active), None)
        if active_model:
            active_model_info = {
                "id": str(active_model.id),
                "name": active_model.model_name,
                "algorithm": active_model.algorithm,
            }

        return {
            "metrics_averages": metrics_averages,
            "active_model": active_model_info,
        }
