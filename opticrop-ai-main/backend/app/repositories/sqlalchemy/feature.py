from typing import Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.feature_metadata import FeatureMetadata
from app.repositories.interfaces.feature import FeatureMetadataRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyFeatureMetadataRepository(SqlAlchemyBaseRepository[FeatureMetadata], FeatureMetadataRepository):
    """Concrete SQLAlchemy implementation of FeatureMetadataRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, FeatureMetadata)

    async def get_by_dataset_id(self, dataset_id: Any) -> List[FeatureMetadata]:
        stmt = select(FeatureMetadata).where(FeatureMetadata.dataset_id == dataset_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_features_batch(self, features: List[FeatureMetadata]) -> List[FeatureMetadata]:
        self.session.add_all(features)
        await self.session.flush()
        for feature in features:
            await self.session.refresh(feature)
        return features
