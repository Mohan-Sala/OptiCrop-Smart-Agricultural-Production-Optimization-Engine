from typing import Any, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.models.model_metric import ModelMetric
from app.repositories.interfaces.model_analytics import ModelAnalyticsRepository


class SqlAlchemyModelAnalyticsRepository(ModelAnalyticsRepository):
    """Concrete SQLAlchemy implementation of ModelAnalyticsRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_lifecycle_status_distribution(self, project_id: Any) -> Dict[str, int]:
        stmt = (
            select(TrainedModel.status, func.count(TrainedModel.id))
            .join(TrainedModel.training_session)
            .join(TrainingSession.dataset)
            .where(Dataset.project_id == project_id)
            .group_by(TrainedModel.status)
        )
        res = await self.session.execute(stmt)
        dist = {"READY": 0, "TRAINING": 0, "FAILED": 0, "ARCHIVED": 0, "DEPRECATED": 0}
        for status, count in res.all():
            dist[status.upper()] = count
        return dist

    async def get_registry_general_statistics(self, project_id: Any) -> Dict[str, Any]:
        stmt = (
            select(ModelMetric.metric_name, func.avg(ModelMetric.metric_value))
            .join(ModelMetric.trained_model)
            .join(TrainedModel.training_session)
            .join(TrainingSession.dataset)
            .where(Dataset.project_id == project_id, TrainedModel.status == "READY")
            .group_by(ModelMetric.metric_name)
        )
        res = await self.session.execute(stmt)
        metrics_averages = {}
        for name, avg_val in res.all():
            metrics_averages[name] = float(avg_val or 0.0)
            
        active_stmt = (
            select(TrainedModel.id, TrainedModel.model_name, TrainedModel.algorithm)
            .join(TrainedModel.training_session)
            .join(TrainingSession.dataset)
            .where(Dataset.project_id == project_id, TrainedModel.is_active == True)
        )
        active_res = await self.session.execute(active_stmt)
        active_row = active_res.first()
        active_model_info = None
        if active_row:
            active_model_info = {
                "id": str(active_row[0]),
                "name": active_row[1],
                "algorithm": active_row[2]
            }
            
        return {
            "metrics_averages": metrics_averages,
            "active_model": active_model_info
        }
