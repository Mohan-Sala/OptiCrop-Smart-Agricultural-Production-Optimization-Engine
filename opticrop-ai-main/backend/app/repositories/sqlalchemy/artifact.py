from typing import Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.preprocessing_artifact import PreprocessingArtifact
from app.repositories.interfaces.artifact import PreprocessingArtifactRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyPreprocessingArtifactRepository(
    SqlAlchemyBaseRepository[PreprocessingArtifact], PreprocessingArtifactRepository
):
    """Concrete SQLAlchemy implementation of PreprocessingArtifactRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, PreprocessingArtifact)

    async def get_by_run_id(self, run_id: Any) -> List[PreprocessingArtifact]:
        stmt = select(PreprocessingArtifact).where(PreprocessingArtifact.preprocessing_run_id == run_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
