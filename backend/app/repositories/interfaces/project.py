from abc import abstractmethod
from typing import Any, List, Optional
from app.models.project import Project
from app.repositories.interfaces.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Abstract interface for Project-related database operations."""

    @abstractmethod
    async def get_by_user_id(self, user_id: Any) -> List[Project]:
        """Retrieves all projects owned by a specific user."""
        pass

    @abstractmethod
    async def get_by_id_and_user_id(self, project_id: Any, user_id: Any) -> Optional[Project]:
        """Retrieves a specific project owned by the user."""
        pass
