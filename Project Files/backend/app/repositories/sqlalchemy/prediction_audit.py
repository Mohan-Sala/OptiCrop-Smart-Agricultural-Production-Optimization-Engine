from typing import Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction_run import PredictionRun
from app.repositories.interfaces.prediction_audit import PredictionAuditRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyPredictionAuditRepository(SqlAlchemyBaseRepository[PredictionRun], PredictionAuditRepository):
    """Concrete SQLAlchemy implementation of PredictionAuditRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, PredictionRun)

    async def get_system_audit_metrics(self, project_id: Any) -> List[PredictionRun]:
        stmt = select(PredictionRun).where(PredictionRun.project_id == project_id).order_by(PredictionRun.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
