from typing import Any, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.login_audit import LoginAudit
from app.repositories.interfaces.login_audit import LoginAuditRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyLoginAuditRepository(SqlAlchemyBaseRepository[LoginAudit], LoginAuditRepository):
    """Concrete SQLAlchemy implementation of LoginAuditRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, LoginAudit)

    async def get_by_user_id(self, user_id: Any, limit: int = 50) -> List[LoginAudit]:
        stmt = (
            select(LoginAudit)
            .where(LoginAudit.user_id == user_id)
            .order_by(desc(LoginAudit.login_time))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
