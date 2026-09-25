import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument
from app.core.roles import UserRole


class User(AppDocument):
    full_name: str
    email: str
    hashed_password: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole = UserRole.FARMER
    bio: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    settings: list = Field(default_factory=list)

    # Password Reset & Email Verification Future-Proofing
    reset_token_hash: Optional[str] = None
    reset_token_expiry: Optional[datetime] = None
    email_verified: bool = False
    verification_token: Optional[str] = None
    verification_token_expiry: Optional[datetime] = None

    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("reset_token_hash", ASCENDING)]),
        ]
