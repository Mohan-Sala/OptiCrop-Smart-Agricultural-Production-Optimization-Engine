import uuid
from datetime import datetime, timezone
from typing import Any, Generic, List, Optional, Type, TypeVar
from beanie import Document
from app.repositories.interfaces.base import BaseRepository

T = TypeVar("T", bound=Document)


def to_uuid(id_val: Any) -> Any:
    """Helper to convert string UUIDs to uuid.UUID objects."""
    if isinstance(id_val, str):
        try:
            return uuid.UUID(id_val)
        except (ValueError, TypeError):
            return id_val
    return id_val


class MongoBaseRepository(BaseRepository[T], Generic[T]):
    """Generic MongoDB / Beanie repository implementing abstract BaseRepository."""

    def __init__(self, model: Type[T], *args, **kwargs):
        self.model = model

    async def get_by_id(self, id: Any) -> Optional[T]:
        if id is None:
            return None
        parsed_id = to_uuid(id)
        doc = await self.model.get(parsed_id)
        if not doc and parsed_id != id:
            doc = await self.model.get(id)
        return doc

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return await self.model.find_all().skip(skip).limit(limit).to_list()

    async def create(self, entity_data: Any) -> T:
        if isinstance(entity_data, self.model):
            await entity_data.insert()
            return entity_data
        elif isinstance(entity_data, dict):
            entity = self.model(**entity_data)
            await entity.insert()
            return entity
        elif hasattr(entity_data, "model_dump"):
            entity = self.model(**entity_data.model_dump())
            await entity.insert()
            return entity
        else:
            entity = self.model(**dict(entity_data))
            await entity.insert()
            return entity

    async def update(self, id: Any, entity_data: Any) -> Optional[T]:
        entity = await self.get_by_id(id)
        if not entity:
            return None
        if isinstance(entity_data, dict):
            update_dict = entity_data
        elif hasattr(entity_data, "model_dump"):
            update_dict = entity_data.model_dump(exclude_unset=True)
        else:
            update_dict = dict(entity_data)

        for key, value in update_dict.items():
            if hasattr(entity, key) and key != "id":
                setattr(entity, key, value)
        if hasattr(entity, "updated_at"):
            setattr(entity, "updated_at", datetime.now(timezone.utc))
        await entity.save()
        return entity

    async def delete(self, id: Any) -> bool:
        entity = await self.get_by_id(id)
        if not entity:
            return False
        await entity.delete()
        return True

    async def save(self) -> None:
        """No-op in MongoDB as Beanie operations are immediately persisted."""
        pass

    @property
    def session(self):
        """Compatibility session handle returning self."""
        return self

    @session.setter
    def session(self, value):
        pass

    async def flush(self) -> None:
        """No-op in MongoDB."""
        pass

    async def commit(self) -> None:
        """No-op in MongoDB."""
        pass

    async def rollback(self) -> None:
        """No-op in MongoDB."""
        pass
