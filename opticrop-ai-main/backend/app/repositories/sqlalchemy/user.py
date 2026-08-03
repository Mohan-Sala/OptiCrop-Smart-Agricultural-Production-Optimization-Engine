from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.interfaces.user import UserRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyUserRepository(SqlAlchemyBaseRepository[User], UserRepository):
    """Concrete SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_reset_token_hash(self, token_hash: str) -> Optional[User]:
        stmt = select(User).where(User.reset_token_hash == token_hash)
        result = await self.session.execute(stmt)
        return result.scalars().first()

