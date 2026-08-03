from typing import Any, List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction_run import PredictionRun
from app.repositories.interfaces.prediction_history import PredictionHistoryRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyPredictionHistoryRepository(SqlAlchemyBaseRepository[PredictionRun], PredictionHistoryRepository):
    """Concrete SQLAlchemy implementation of PredictionHistoryRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, PredictionRun)

    async def list_history_paginated(
        self,
        user_id: Any,
        project_id: Optional[Any] = None,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
    ) -> List[PredictionRun]:
        stmt = select(PredictionRun).where(PredictionRun.user_id == user_id)
        
        if project_id is not None:
            stmt = stmt.where(PredictionRun.project_id == project_id)
        if status is not None:
            stmt = stmt.where(PredictionRun.status == status)

        stmt = stmt.order_by(PredictionRun.created_at.desc())
        
        # Apply pagination offset
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
