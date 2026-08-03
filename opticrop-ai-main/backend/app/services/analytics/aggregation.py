import uuid
from typing import Dict, Any
from app.repositories.interfaces.project_analytics import ProjectAnalyticsRepository
from app.repositories.interfaces.dataset_analytics import DatasetAnalyticsRepository
from app.repositories.interfaces.training_analytics import TrainingAnalyticsRepository
from app.repositories.interfaces.model_analytics import ModelAnalyticsRepository


class AggregationService:
    """Combines project metrics, storage sizes, and models lifecycles from analytics repos."""

    def __init__(
        self,
        project_repo: ProjectAnalyticsRepository,
        dataset_repo: DatasetAnalyticsRepository,
        training_repo: TrainingAnalyticsRepository,
        model_repo: ModelAnalyticsRepository
    ):
        self.project_repo = project_repo
        self.dataset_repo = dataset_repo
        self.training_repo = training_repo
        self.model_repo = model_repo

    async def aggregate_project_summary(self, project_id: uuid.UUID) -> Dict[str, Any]:
        counts = await self.project_repo.get_overview_counts(project_id)
        storage = await self.project_repo.get_storage_usage(project_id)
        stages = await self.dataset_repo.get_dataset_stages_distribution(project_id)
        durations = await self.training_repo.get_training_duration_metrics(project_id)
        reg_stats = await self.model_repo.get_registry_general_statistics(project_id)
        
        return {
            "project_id": project_id,
            "datasets_count": counts["datasets_count"],
            "preprocessing_runs_count": counts["preprocessing_runs_count"],
            "training_sessions_count": counts["training_sessions_count"],
            "registered_models_count": counts["registered_models_count"],
            "storage_usage_bytes": storage,
            "dataset_stages": stages,
            "training_durations": durations,
            "active_model": reg_stats["active_model"],
            "metrics_averages": reg_stats["metrics_averages"]
        }
