from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.hyperparameter_set import HyperparameterSet
from app.repositories.interfaces.hyperparameter import HyperparameterSetRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyHyperparameterSetRepository(SqlAlchemyBaseRepository[HyperparameterSet], HyperparameterSetRepository):
    """Concrete SQLAlchemy implementation of HyperparameterSetRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, HyperparameterSet)

    async def get_by_model_id(self, model_id: Any) -> Optional[HyperparameterSet]:
        stmt = select(HyperparameterSet).where(HyperparameterSet.trained_model_id == model_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
