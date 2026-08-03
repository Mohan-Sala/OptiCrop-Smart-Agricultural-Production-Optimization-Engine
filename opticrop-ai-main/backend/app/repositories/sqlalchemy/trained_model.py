from typing import Any, List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.trained_model import TrainedModel
from app.models.training_session import TrainingSession
from app.models.dataset import Dataset
from app.models.dataset_preprocessing import DatasetPreprocessing
from app.repositories.interfaces.trained_model import TrainedModelRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyTrainedModelRepository(SqlAlchemyBaseRepository[TrainedModel], TrainedModelRepository):
    """Concrete SQLAlchemy implementation of TrainedModelRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, TrainedModel)

    async def get_by_id(self, id: Any) -> Optional[TrainedModel]:
        stmt = (
            select(TrainedModel)
            .options(
                selectinload(TrainedModel.metrics),
                selectinload(TrainedModel.evaluation_report),
                selectinload(TrainedModel.hyperparameter_set),
                selectinload(TrainedModel.training_session).selectinload(TrainingSession.dataset).selectinload(Dataset.preprocessing_runs).selectinload(DatasetPreprocessing.artifacts),
                selectinload(TrainedModel.training_session).selectinload(TrainingSession.dataset).selectinload(Dataset.statistics),
            )
            .where(TrainedModel.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_project_id(self, project_id: Any) -> List[TrainedModel]:
        stmt = (
            select(TrainedModel)
            .options(
                selectinload(TrainedModel.metrics),
                selectinload(TrainedModel.evaluation_report),
                selectinload(TrainedModel.hyperparameter_set),
                selectinload(TrainedModel.training_session).selectinload(TrainingSession.dataset).selectinload(Dataset.preprocessing_runs).selectinload(DatasetPreprocessing.artifacts),
                selectinload(TrainedModel.training_session).selectinload(TrainingSession.dataset).selectinload(Dataset.statistics),
            )
            .join(TrainedModel.training_session)
            .join(TrainingSession.dataset)
            .where(Dataset.project_id == project_id)
            .order_by(TrainedModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_model(self, project_id: Any) -> Optional[TrainedModel]:
        stmt = (
            select(TrainedModel)
            .options(
                selectinload(TrainedModel.metrics),
                selectinload(TrainedModel.evaluation_report),
                selectinload(TrainedModel.hyperparameter_set),
                selectinload(TrainedModel.training_session).selectinload(TrainingSession.dataset).selectinload(Dataset.preprocessing_runs).selectinload(DatasetPreprocessing.artifacts),
                selectinload(TrainedModel.training_session).selectinload(TrainingSession.dataset).selectinload(Dataset.statistics),
            )
            .join(TrainedModel.training_session)
            .join(TrainingSession.dataset)
            .where(Dataset.project_id == project_id, TrainedModel.is_active == True)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def deactivate_all_in_project(self, project_id: Any) -> None:
        subquery = (
            select(TrainedModel.id)
            .join(TrainedModel.training_session)
            .join(TrainingSession.dataset)
            .where(Dataset.project_id == project_id)
        )
        stmt = (
            update(TrainedModel)
            .where(TrainedModel.id.in_(subquery))
            .values(is_active=False)
        )
        await self.session.execute(stmt)
