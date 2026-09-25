import uuid
from datetime import datetime
from typing import Optional
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class RefreshToken(AppDocument):
    user_id: uuid.UUID
    token_hash: str
    device_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    expires_at: datetime
    revoked_at: Optional[datetime] = None
    is_active: bool = True

    class Settings:
        name = "refresh_tokens"
        indexes = [
            IndexModel([("token_hash", ASCENDING)], unique=True),
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("is_active", ASCENDING)]),
        ]
