from typing import Any, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dataset_preprocessing import DatasetPreprocessing
from app.repositories.interfaces.preprocessing import PreprocessingRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyPreprocessingRepository(SqlAlchemyBaseRepository[DatasetPreprocessing], PreprocessingRepository):
    """Concrete SQLAlchemy implementation of PreprocessingRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, DatasetPreprocessing)

    async def get_by_id(self, id: Any) -> Optional[DatasetPreprocessing]:
        stmt = (
            select(DatasetPreprocessing)
            .options(selectinload(DatasetPreprocessing.artifacts))
            .where(DatasetPreprocessing.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_dataset_id(self, dataset_id: Any) -> List[DatasetPreprocessing]:
        stmt = (
            select(DatasetPreprocessing)
            .options(selectinload(DatasetPreprocessing.artifacts))
            .where(DatasetPreprocessing.dataset_id == dataset_id)
            .order_by(DatasetPreprocessing.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_hash_and_user(self, config_hash: str, user_id: Any) -> Optional[DatasetPreprocessing]:
        stmt = (
            select(DatasetPreprocessing)
            .options(selectinload(DatasetPreprocessing.artifacts))
            .where(
                DatasetPreprocessing.preprocessing_hash == config_hash,
                DatasetPreprocessing.user_id == user_id,
                DatasetPreprocessing.status == "COMPLETED",
            )
            .order_by(DatasetPreprocessing.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
