import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, delete, and_
from app.models.drift_snapshot import DriftSnapshot
from app.core.enums import DriftStatus
from app.repositories.interfaces.drift import DriftRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyDriftRepository(SqlAlchemyBaseRepository[DriftSnapshot], DriftRepository):
    """Concrete SQLAlchemy implementation of DriftRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, DriftSnapshot)

    async def get_latest_by_model(self, model_id: uuid.UUID) -> Optional[DriftSnapshot]:
        stmt = (
            select(DriftSnapshot)
            .where(
                and_(
                    DriftSnapshot.model_id == model_id,
                    DriftSnapshot.status == DriftStatus.COMPLETED,
                )
            )
            .order_by(DriftSnapshot.computed_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_snapshots_by_project(
        self, project_id: uuid.UUID, limit: int = 100
    ) -> List[DriftSnapshot]:
        stmt = (
            select(DriftSnapshot)
            .where(DriftSnapshot.project_id == project_id)
            .order_by(DriftSnapshot.computed_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def prune_snapshots(self, before: datetime, exclude_active_model_ids: List[uuid.UUID]) -> int:
        stmt = delete(DriftSnapshot).where(
            and_(
                DriftSnapshot.computed_at < before,
                ~DriftSnapshot.model_id.in_(exclude_active_model_ids),
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount
