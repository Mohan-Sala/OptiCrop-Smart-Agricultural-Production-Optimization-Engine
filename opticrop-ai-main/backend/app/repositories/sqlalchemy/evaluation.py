from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.evaluation_report import EvaluationReport
from app.repositories.interfaces.evaluation import EvaluationReportRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyEvaluationReportRepository(SqlAlchemyBaseRepository[EvaluationReport], EvaluationReportRepository):
    """Concrete SQLAlchemy implementation of EvaluationReportRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, EvaluationReport)

    async def get_by_model_id(self, model_id: Any) -> Optional[EvaluationReport]:
        stmt = select(EvaluationReport).where(EvaluationReport.trained_model_id == model_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
