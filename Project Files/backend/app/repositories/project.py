from abc import abstractmethod
from typing import List
from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Abstract interface for Project-related database operations."""

    @abstractmethod
    async def get_by_user_id(self, user_id: Any) -> List[Project]:
        """Retrieves all projects owned by a specific user."""
        pass
