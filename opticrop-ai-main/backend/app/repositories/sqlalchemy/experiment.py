from typing import Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.training_experiment import TrainingExperiment
from app.repositories.interfaces.experiment import ExperimentRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyExperimentRepository(SqlAlchemyBaseRepository[TrainingExperiment], ExperimentRepository):
    """Concrete SQLAlchemy implementation of ExperimentRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, TrainingExperiment)

    async def get_by_project_id(self, project_id: Any) -> List[TrainingExperiment]:
        stmt = select(TrainingExperiment).where(TrainingExperiment.project_id == project_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
