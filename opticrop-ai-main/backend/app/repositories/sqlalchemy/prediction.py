from typing import Any, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction_run import PredictionRun, PredictionStatus
from app.repositories.interfaces.prediction import PredictionRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyPredictionRepository(SqlAlchemyBaseRepository[PredictionRun], PredictionRepository):
    """Concrete SQLAlchemy implementation of PredictionRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, PredictionRun)

    async def get_by_id(self, id: Any) -> Optional[PredictionRun]:
        stmt = select(PredictionRun).where(PredictionRun.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_idempotency_key(self, user_id: Any, idempotency_key: str) -> Optional[PredictionRun]:
        stmt = select(PredictionRun).where(
            and_(
                PredictionRun.user_id == user_id,
                PredictionRun.idempotency_key == idempotency_key,
                PredictionRun.status == PredictionStatus.COMPLETED
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_request_hash(self, model_id: Any, request_hash: str) -> Optional[PredictionRun]:
        stmt = select(PredictionRun).where(
            and_(
                PredictionRun.model_id == model_id,
                PredictionRun.request_hash == request_hash,
                PredictionRun.status == PredictionStatus.COMPLETED
            )
        ).order_by(PredictionRun.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_completed_by_model(self, model_id: Any, limit: int = 500) -> list[PredictionRun]:
        stmt = (
            select(PredictionRun)
            .where(
                and_(
                    PredictionRun.model_id == model_id,
                    PredictionRun.status == PredictionStatus.COMPLETED
                )
            )
            .order_by(PredictionRun.prediction_timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
