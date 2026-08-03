from typing import Any, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset
from app.models.dataset_preprocessing import DatasetPreprocessing
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.repositories.interfaces.project_analytics import ProjectAnalyticsRepository


class SqlAlchemyProjectAnalyticsRepository(ProjectAnalyticsRepository):
    """Concrete SQLAlchemy implementation of ProjectAnalyticsRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_overview_counts(self, project_id: Any) -> Dict[str, Any]:
        # Count datasets
        ds_stmt = select(func.count(Dataset.id)).where(Dataset.project_id == project_id, Dataset.is_deleted == False)
        ds_res = await self.session.execute(ds_stmt)
        datasets_count = ds_res.scalar() or 0

        # Count preprocessing runs
        prep_stmt = select(func.count(DatasetPreprocessing.id)).where(DatasetPreprocessing.project_id == project_id)
        prep_res = await self.session.execute(prep_stmt)
        prep_count = prep_res.scalar() or 0

        # Count training runs
        sess_stmt = select(func.count(TrainingSession.id)).join(TrainingSession.dataset).where(
            Dataset.project_id == project_id
        )
        sess_res = await self.session.execute(sess_stmt)
        training_count = sess_res.scalar() or 0

        # Count registered models
        mod_stmt = select(func.count(TrainedModel.id)).join(TrainedModel.training_session).join(TrainingSession.dataset).where(
            Dataset.project_id == project_id
        )
        mod_res = await self.session.execute(mod_stmt)
        models_count = mod_res.scalar() or 0

        return {
            "datasets_count": datasets_count,
            "preprocessing_runs_count": prep_count,
            "training_sessions_count": training_count,
            "registered_models_count": models_count,
        }

    async def get_storage_usage(self, project_id: Any) -> int:
        stmt = select(func.sum(Dataset.size)).where(Dataset.project_id == project_id, Dataset.is_deleted == False)
        res = await self.session.execute(stmt)
        return res.scalar() or 0
