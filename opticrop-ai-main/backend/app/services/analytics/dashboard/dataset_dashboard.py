import uuid
from typing import Dict, Any
from app.repositories.interfaces.dataset_analytics import DatasetAnalyticsRepository


class DatasetDashboardService:
    """Aggregates dataset-specific counts, distribution sizes, and growth histories."""

    def __init__(self, repo: DatasetAnalyticsRepository):
        self.repo = repo

    async def get_dashboard_data(self, project_id: uuid.UUID) -> Dict[str, Any]:
        stages = await self.repo.get_dataset_stages_distribution(project_id)
        growth = await self.repo.get_datasets_growth_history(project_id)
        return {
            "dataset_stages": stages,
            "growth_history": growth
        }
