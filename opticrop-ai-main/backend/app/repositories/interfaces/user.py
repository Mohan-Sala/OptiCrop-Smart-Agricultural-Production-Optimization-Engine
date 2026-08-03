from abc import abstractmethod
from typing import Optional
from app.models.user import User
from app.repositories.interfaces.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Abstract interface for User-related database operations."""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieves a user profile matching the given email address."""
        pass

    @abstractmethod
    async def get_by_reset_token_hash(self, token_hash: str) -> Optional[User]:
        """Retrieves a user profile matching the given reset token hash."""
        pass

