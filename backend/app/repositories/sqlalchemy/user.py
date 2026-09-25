from typing import Optional
from app.models.user import User
from app.repositories.interfaces.user import UserRepository
from app.repositories.mongodb.user import MongoUserRepository


class SqlAlchemyUserRepository(MongoUserRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyUserRepository calls to MongoUserRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)

