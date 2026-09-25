from typing import Any, List, Optional, Type, TypeVar
from app.repositories.interfaces.base import BaseRepository
from app.repositories.mongodb.base import MongoBaseRepository

T = TypeVar("T")


class SqlAlchemyBaseRepository(MongoBaseRepository[T]):
    """Compatibility adapter redirecting legacy SqlAlchemyBaseRepository to MongoBaseRepository."""

    def __init__(self, session=None, model: Optional[Type[T]] = None, *args, **kwargs):
        self.session = session
        if model is not None:
            super().__init__(model, *args, **kwargs)
