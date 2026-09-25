from datetime import datetime, timezone
from typing import Any, Optional
from app.models.refresh_token import RefreshToken
from app.repositories.interfaces.refresh_token import RefreshTokenRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoRefreshTokenRepository(MongoBaseRepository[RefreshToken], RefreshTokenRepository):
    """Concrete MongoDB / Beanie implementation of RefreshTokenRepository."""

    def __init__(self):
        super().__init__(RefreshToken)

    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        return await RefreshToken.find_one(RefreshToken.token_hash == token_hash)

    async def revoke_by_token_hash(self, token_hash: str) -> bool:
        token = await RefreshToken.find_one(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_active == True,
        )
        if not token:
            return False
        token.is_active = False
        token.revoked_at = datetime.now(timezone.utc)
        await token.save()
        return True

    async def revoke_all_for_user(self, user_id: Any) -> bool:
        parsed_user_id = to_uuid(user_id)
        result = await RefreshToken.find(
            RefreshToken.user_id == parsed_user_id,
            RefreshToken.is_active == True,
        ).update(
            {"$set": {"is_active": False, "revoked_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0

    async def clean_expired_tokens(self) -> int:
        now = datetime.now(timezone.utc)
        result = await RefreshToken.find({
            "$or": [
                {"expires_at": {"$lt": now}},
                {"is_active": False},
            ]
        }).delete()
        return result.deleted_count
