from abc import abstractmethod
from typing import Any, Optional
from app.models.refresh_token import RefreshToken
from app.repositories.interfaces.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Abstract interface for RefreshToken-related database operations."""

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Retrieves a persistent RefreshToken matching the SHA-256 hash."""
        pass

    @abstractmethod
    async def revoke_by_token_hash(self, token_hash: str) -> bool:
        """Revokes (soft deletes) a specific refresh token session."""
        pass

    @abstractmethod
    async def revoke_all_for_user(self, user_id: Any) -> bool:
        """Revokes all active refresh tokens associated with a specific user (Logout All)."""
        pass

    @abstractmethod
    async def clean_expired_tokens(self) -> int:
        """Purges expired refresh token records from database."""
        pass
