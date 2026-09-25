from abc import abstractmethod
from typing import Any, List
from app.models.notification import Notification
from app.repositories.interfaces.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Abstract interface for Notification-related database operations."""

    @abstractmethod
    async def get_unread_by_user_id(self, user_id: Any) -> List[Notification]:
        """Retrieves unread notifications for a specific user."""
        pass

    @abstractmethod
    async def mark_all_as_read(self, user_id: Any) -> bool:
        """Flags all active notifications for a user as read."""
        pass
