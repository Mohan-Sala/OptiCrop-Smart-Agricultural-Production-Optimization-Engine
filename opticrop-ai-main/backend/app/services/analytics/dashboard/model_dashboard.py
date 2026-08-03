import uuid
from typing import Dict, Any
from app.repositories.interfaces.model_analytics import ModelAnalyticsRepository


class ModelDashboardService:
    """Aggregates model registry sizes, active model versions, and general accuracy metric summaries."""

    def __init__(self, repo: ModelAnalyticsRepository):
        self.repo = repo

    async def get_dashboard_data(self, project_id: uuid.UUID) -> Dict[str, Any]:
        lifecycles = await self.repo.get_lifecycle_status_distribution(project_id)
        general_stats = await self.repo.get_registry_general_statistics(project_id)
        return {
            "lifecycle_distribution": lifecycles,
            "registry_statistics": general_stats
        }
