import uuid
from datetime import datetime
from typing import List
from sqlalchemy import select, delete, and_
from app.models.external_telemetry import ExternalTelemetryLog
from app.repositories.interfaces.telemetry import TelemetryRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyTelemetryRepository(SqlAlchemyBaseRepository[ExternalTelemetryLog], TelemetryRepository):
    """Concrete SQLAlchemy implementation of TelemetryRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ExternalTelemetryLog)

    async def list_by_project_and_range(
        self, project_id: uuid.UUID, start: datetime, end: datetime
    ) -> List[ExternalTelemetryLog]:
        stmt = (
            select(ExternalTelemetryLog)
            .where(
                and_(
                    ExternalTelemetryLog.project_id == project_id,
                    ExternalTelemetryLog.recorded_at >= start,
                    ExternalTelemetryLog.recorded_at <= end,
                )
            )
            .order_by(ExternalTelemetryLog.recorded_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def prune_telemetry(self, before: datetime) -> int:
        stmt = delete(ExternalTelemetryLog).where(ExternalTelemetryLog.recorded_at < before)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount
