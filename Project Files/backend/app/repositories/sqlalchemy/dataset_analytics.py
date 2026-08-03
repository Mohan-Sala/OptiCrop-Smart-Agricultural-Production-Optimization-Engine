from typing import Any, List, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset
from app.core.enums import DatasetStage
from app.repositories.interfaces.dataset_analytics import DatasetAnalyticsRepository


class SqlAlchemyDatasetAnalyticsRepository(DatasetAnalyticsRepository):
    """Concrete SQLAlchemy implementation of DatasetAnalyticsRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_dataset_stages_distribution(self, project_id: Any) -> Dict[str, int]:
        stmt = (
            select(Dataset.dataset_stage, func.count(Dataset.id))
            .where(Dataset.project_id == project_id, Dataset.is_deleted == False)
            .group_by(Dataset.dataset_stage)
        )
        res = await self.session.execute(stmt)
        dist = {stage.name: 0 for stage in DatasetStage}
        for stage, count in res.all():
            dist[stage.name] = count
        return dist

    async def get_datasets_growth_history(self, project_id: Any) -> List[Dict[str, Any]]:
        stmt = (
            select(Dataset.created_at, Dataset.size, Dataset.version)
            .where(Dataset.project_id == project_id, Dataset.is_deleted == False)
            .order_by(Dataset.created_at.asc())
        )
        res = await self.session.execute(stmt)
        history = []
        for created_at, size, version in res.all():
            history.append({
                "date": created_at.isoformat(),
                "size_bytes": size,
                "version": version
            })
        return history
