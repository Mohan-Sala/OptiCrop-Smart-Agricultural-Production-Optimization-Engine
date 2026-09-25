import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class LoginAudit(AppDocument):
    user_id: Optional[uuid.UUID] = None
    login_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    logout_time: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_name: Optional[str] = None
    success: bool = True
    failure_reason: Optional[str] = None

    class Settings:
        name = "login_audits"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("success", ASCENDING)]),
        ]
