from typing import Any, List, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset
from app.models.training_session import TrainingSession
from app.models.training_experiment import TrainingExperiment
from app.repositories.interfaces.training_analytics import TrainingAnalyticsRepository


class SqlAlchemyTrainingAnalyticsRepository(TrainingAnalyticsRepository):
    """Concrete SQLAlchemy implementation of TrainingAnalyticsRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_session_statuses_count(self, project_id: Any) -> Dict[str, int]:
        stmt = (
            select(TrainingSession.status, func.count(TrainingSession.id))
            .join(TrainingSession.dataset)
            .where(Dataset.project_id == project_id)
            .group_by(TrainingSession.status)
        )
        res = await self.session.execute(stmt)
        # default statuses
        counts = {"PENDING": 0, "TRAINING": 0, "COMPLETED": 0, "FAILED": 0}
        for status, count in res.all():
            counts[status.upper()] = count
        return counts

    async def get_training_duration_metrics(self, project_id: Any) -> Dict[str, float]:
        stmt = (
            select(
                func.avg(TrainingSession.training_time),
                func.min(TrainingSession.training_time),
                func.max(TrainingSession.training_time)
            )
            .join(TrainingSession.dataset)
            .where(Dataset.project_id == project_id, TrainingSession.status == "COMPLETED")
        )
        res = await self.session.execute(stmt)
        avg_t, min_t, max_t = res.first() or (0.0, 0.0, 0.0)
        return {
            "average_time": float(avg_t or 0.0),
            "minimum_time": float(min_t or 0.0),
            "maximum_time": float(max_t or 0.0)
        }

    async def get_experiments_summary(self, project_id: Any) -> List[Dict[str, Any]]:
        stmt = (
            select(
                TrainingExperiment.id,
                TrainingExperiment.name,
                TrainingExperiment.description,
                func.count(TrainingSession.id)
            )
            .outerjoin(TrainingSession, TrainingSession.experiment_id == TrainingExperiment.id)
            .where(TrainingExperiment.project_id == project_id)
            .group_by(TrainingExperiment.id, TrainingExperiment.name, TrainingExperiment.description)
        )
        res = await self.session.execute(stmt)
        summary = []
        for exp_id, name, desc, count in res.all():
            summary.append({
                "experiment_id": str(exp_id),
                "name": name,
                "description": desc,
                "sessions_count": count
            })
        return summary
