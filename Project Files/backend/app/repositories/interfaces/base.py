from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository interface enforcing structural consistency."""

    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Retrieves a single entity by its unique identifier."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Retrieves a paginated list of entities."""
        pass

    @abstractmethod
    async def create(self, entity_data: Any) -> T:
        """Persists a new entity record."""
        pass

    @abstractmethod
    async def update(self, id: Any, entity_data: Any) -> Optional[T]:
        """Updates an existing entity record."""
        pass

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Deletes an entity record by its unique identifier."""
        pass
