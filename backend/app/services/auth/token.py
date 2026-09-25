import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Tuple
from app.models.refresh_token import RefreshToken
from app.repositories.interfaces.refresh_token import RefreshTokenRepository
from app.utils.exceptions import AuthenticationException


class TokenService:
    """Orchestrates high-level Refresh Token persistence, validation, and rotation."""

    def __init__(self, token_repo: RefreshTokenRepository):
        self.token_repo = token_repo

    def hash_token(self, token: str) -> str:
        """Computes SHA-256 hash of a plaintext token string."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def create_refresh_token(
        self,
        user_id: Any,
        device_name: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> str:
        """Generates, hashes, and registers a secure refresh token."""
        raw_token = secrets.token_hex(32)
        token_hash = self.hash_token(raw_token)

        # Refresh token lifespan: 7 days
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        token_record = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            device_name=device_name,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_active=True,
        )
        await self.token_repo.create(token_record)
        return raw_token

    async def verify_and_rotate_refresh_token(
        self,
        raw_token: str,
        device_name: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[str, Any]:
        """Rotates a refresh token, revoking the old one and returning a new one.

        Protects against refresh token reuse.
        """
        token_hash = self.hash_token(raw_token)
        token_record = await self.token_repo.get_by_token_hash(token_hash)

        if not token_record or not token_record.is_active or token_record.revoked_at is not None:
            raise AuthenticationException("Authentication failed: invalid or revoked refresh token.")

        expires_at = token_record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            await self.token_repo.revoke_by_token_hash(token_hash)
            raise AuthenticationException("Credentials expired: refresh token expired.")

        # Revoke the used token immediately
        await self.token_repo.revoke_by_token_hash(token_hash)

        # Generate a new rotated token for the user session
        new_raw_token = await self.create_refresh_token(
            user_id=token_record.user_id,
            device_name=device_name,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return new_raw_token, token_record.user_id

    async def revoke_refresh_token(self, raw_token: str) -> bool:
        """Revokes a refresh token session using its plaintext value."""
        token_hash = self.hash_token(raw_token)
        return await self.token_repo.revoke_by_token_hash(token_hash)

    async def revoke_all_for_user(self, user_id: Any) -> bool:
        """Revokes all active refresh tokens associated with a specific user."""
        return await self.token_repo.revoke_all_for_user(user_id)
