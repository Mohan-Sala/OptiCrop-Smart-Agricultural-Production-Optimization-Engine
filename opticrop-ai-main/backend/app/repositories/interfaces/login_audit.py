from abc import abstractmethod
from typing import Any, List
from app.models.login_audit import LoginAudit
from app.repositories.interfaces.base import BaseRepository


class LoginAuditRepository(BaseRepository[LoginAudit]):
    """Abstract interface for LoginAudit-related database operations."""

    @abstractmethod
    async def get_by_user_id(self, user_id: Any, limit: int = 50) -> List[LoginAudit]:
        """Retrieves authentication logs associated with a user."""
        pass
