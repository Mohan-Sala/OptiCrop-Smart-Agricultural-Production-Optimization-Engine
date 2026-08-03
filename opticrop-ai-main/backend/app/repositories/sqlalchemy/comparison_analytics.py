from typing import Any, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trained_model import TrainedModel
from app.models.training_session import TrainingSession
from app.repositories.interfaces.comparison_analytics import ComparisonAnalyticsRepository


class SqlAlchemyComparisonAnalyticsRepository(ComparisonAnalyticsRepository):
    """Concrete SQLAlchemy implementation of ComparisonAnalyticsRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_models_by_ids(self, model_ids: List[Any]) -> List[TrainedModel]:
        stmt = (
            select(TrainedModel)
            .options(
                selectinload(TrainedModel.metrics),
                selectinload(TrainedModel.evaluation_report),
                selectinload(TrainedModel.hyperparameter_set),
                selectinload(TrainedModel.training_session).selectinload(TrainingSession.dataset),
            )
            .where(TrainedModel.id.in_(model_ids))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
