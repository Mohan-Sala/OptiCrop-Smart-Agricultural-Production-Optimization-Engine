from typing import Any, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.interfaces.base import BaseRepository

T = TypeVar("T")


class SqlAlchemyBaseRepository(BaseRepository[T]):
    """Generic SQLAlchemy repository class implementing abstract BaseRepository."""

    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: Any) -> Optional[T]:
        return await self.session.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, id: Any, entity_data: dict) -> Optional[T]:
        entity = await self.get_by_id(id)
        if not entity:
            return None
        for key, value in entity_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, id: Any) -> bool:
        entity = await self.get_by_id(id)
        if not entity:
            return False
        await self.session.delete(entity)
        await self.session.flush()
        return True
    
    async def save(self) -> None:
        """Helper to flush or commit local session state."""
        await self.session.flush()
