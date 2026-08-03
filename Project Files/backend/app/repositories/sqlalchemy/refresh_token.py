from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken
from app.repositories.interfaces.refresh_token import RefreshTokenRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyRefreshTokenRepository(SqlAlchemyBaseRepository[RefreshToken], RefreshTokenRepository):
    """Concrete SQLAlchemy implementation of RefreshTokenRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, RefreshToken)

    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def revoke_by_token_hash(self, token_hash: str) -> bool:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash, RefreshToken.is_active == True)
            .values(is_active=False, revoked_at=datetime.now(timezone.utc))
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def revoke_all_for_user(self, user_id: Any) -> bool:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_active == True)
            .values(is_active=False, revoked_at=datetime.now(timezone.utc))
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def clean_expired_tokens(self) -> int:
        stmt = delete(RefreshToken).where(
            (RefreshToken.expires_at < datetime.now(timezone.utc)) | (RefreshToken.is_active == False)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount
