from typing import Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.repositories.interfaces.project import ProjectRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyProjectRepository(SqlAlchemyBaseRepository[Project], ProjectRepository):
    """Concrete SQLAlchemy implementation of ProjectRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Project)

    async def get_by_user_id(self, user_id: Any) -> List[Project]:
        stmt = select(Project).where(Project.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_and_user_id(self, project_id: Any, user_id: Any) -> Optional[Project]:
        """Retrieves a specific project if it belongs to the user."""
        stmt = select(Project).where(Project.id == project_id, Project.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
