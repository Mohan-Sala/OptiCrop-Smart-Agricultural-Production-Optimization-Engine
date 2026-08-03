import uuid
from typing import Dict, Any
from app.repositories.interfaces.training_analytics import TrainingAnalyticsRepository


class TrainingDashboardService:
    """Aggregates training sessions count histories, completed run milestones, and experiment metrics."""

    def __init__(self, repo: TrainingAnalyticsRepository):
        self.repo = repo

    async def get_dashboard_data(self, project_id: uuid.UUID) -> Dict[str, Any]:
        statuses = await self.repo.get_session_statuses_count(project_id)
        durations = await self.repo.get_training_duration_metrics(project_id)
        experiments = await self.repo.get_experiments_summary(project_id)
        return {
            "session_statuses": statuses,
            "duration_metrics": durations,
            "experiments_summary": experiments
        }
