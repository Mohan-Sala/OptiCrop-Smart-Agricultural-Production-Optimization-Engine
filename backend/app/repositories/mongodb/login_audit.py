from typing import Any, List
from app.models.login_audit import LoginAudit
from app.repositories.interfaces.login_audit import LoginAuditRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoLoginAuditRepository(MongoBaseRepository[LoginAudit], LoginAuditRepository):
    """Concrete MongoDB / Beanie implementation of LoginAuditRepository."""

    def __init__(self):
        super().__init__(LoginAudit)

    async def get_by_user_id(self, user_id: Any, limit: int = 50) -> List[LoginAudit]:
        parsed_user_id = to_uuid(user_id)
        return await LoginAudit.find(
            LoginAudit.user_id == parsed_user_id
        ).sort("-login_time").limit(limit).to_list()
