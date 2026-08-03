from typing import Any
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repositories.interfaces.user import UserRepository
from app.services.auth.password import validate_password_strength
from app.utils.exceptions import ValidationException


class ProfileService:
    """Orchestrates updates to User profile properties and password modifications."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def update_profile(self, user_id: Any, profile_data: dict) -> User:
        """Modifies user profile details, blocking modifications to read-only fields."""
        # Enforce read-only locks on core fields
        read_only = {
            "id",
            "email",
            "role",
            "hashed_password",
            "created_at",
            "updated_at",
            "last_login",
        }
        filtered_data = {k: v for k, v in profile_data.items() if k not in read_only}

        user = await self.user_repo.update(user_id, filtered_data)
        if not user:
            raise ValidationException("Update failed: user profile not found.")
        return user

    async def change_password(self, user_id: Any, old_password: str, new_password: str) -> None:
        """Validates current password and updates it to the new hashed password."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValidationException("Action failed: user profile not found.")

        if not verify_password(old_password, user.hashed_password):
            raise ValidationException("Action failed: incorrect current password.")

        # Enforce standard password rules
        validate_password_strength(new_password)

        new_hash = get_password_hash(new_password)
        await self.user_repo.update(user_id, {"hashed_password": new_hash})
