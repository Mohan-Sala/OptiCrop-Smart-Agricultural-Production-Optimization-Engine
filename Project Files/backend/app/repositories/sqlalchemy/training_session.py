from typing import Any, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.training_session import TrainingSession
from app.repositories.interfaces.training_session import TrainingSessionRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyTrainingSessionRepository(SqlAlchemyBaseRepository[TrainingSession], TrainingSessionRepository):
    """Concrete SQLAlchemy implementation of TrainingSessionRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, TrainingSession)

    async def get_by_id(self, id: Any) -> Optional[TrainingSession]:
        stmt = (
            select(TrainingSession)
            .options(selectinload(TrainingSession.trained_models))
            .where(TrainingSession.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_project_id(self, project_id: Any) -> List[TrainingSession]:
        stmt = (
            select(TrainingSession)
            .options(selectinload(TrainingSession.trained_models))
            .join(TrainingSession.dataset)
            .where(TrainingSession.dataset.has(project_id=project_id))
            .order_by(TrainingSession.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_hash_and_user(self, config_hash: str, user_id: Any) -> Optional[TrainingSession]:
        stmt = (
            select(TrainingSession)
            .options(selectinload(TrainingSession.trained_models))
            .where(
                TrainingSession.config_hash == config_hash,
                TrainingSession.user_id == user_id,
                TrainingSession.status == "COMPLETED",
            )
            .order_by(TrainingSession.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
