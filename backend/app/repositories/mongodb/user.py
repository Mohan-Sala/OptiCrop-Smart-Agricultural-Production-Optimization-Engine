from typing import Optional
from app.models.user import User
from app.repositories.interfaces.user import UserRepository
from app.repositories.mongodb.base import MongoBaseRepository


class MongoUserRepository(MongoBaseRepository[User], UserRepository):
    """Concrete MongoDB / Beanie implementation of UserRepository."""

    def __init__(self, *args, **kwargs):
        super().__init__(User, *args, **kwargs)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await User.find_one(User.email == email)

    async def get_by_reset_token_hash(self, token_hash: str) -> Optional[User]:
        return await User.find_one(User.reset_token_hash == token_hash)
