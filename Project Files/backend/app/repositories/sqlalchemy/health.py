from datetime import datetime
from typing import List
from sqlalchemy import select, delete
from app.models.monitoring_health_log import MonitoringHealthLog
from app.repositories.interfaces.health import HealthRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyHealthRepository(SqlAlchemyBaseRepository[MonitoringHealthLog], HealthRepository):
    """Concrete SQLAlchemy implementation of HealthRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, MonitoringHealthLog)

    async def list_health_history(self, limit: int = 100) -> List[MonitoringHealthLog]:
        stmt = (
            select(MonitoringHealthLog)
            .order_by(MonitoringHealthLog.recorded_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def prune_health_logs(self, before: datetime) -> int:
        stmt = delete(MonitoringHealthLog).where(MonitoringHealthLog.recorded_at < before)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount
