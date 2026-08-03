from typing import Any, List, Optional, Tuple
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dataset import Dataset
from app.core.enums import DatasetStatus, DatasetStage
from app.repositories.interfaces.dataset import DatasetRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository


class SqlAlchemyDatasetRepository(SqlAlchemyBaseRepository[Dataset], DatasetRepository):
    """Concrete SQLAlchemy implementation of DatasetRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Dataset)

    async def get_by_id(self, id: Any) -> Optional[Dataset]:
        """Eagerly loads statistics when retrieving by ID to avoid lazy loading issues."""
        stmt = select(Dataset).options(
            selectinload(Dataset.statistics),
            selectinload(Dataset.feature_catalog)
        ).where(Dataset.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_project_id(self, project_id: Any) -> List[Dataset]:
        stmt = select(Dataset).options(
            selectinload(Dataset.statistics),
            selectinload(Dataset.feature_catalog)
        ).where(
            Dataset.project_id == project_id, 
            Dataset.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_and_user_id(self, dataset_id: Any, user_id: Any) -> Optional[Dataset]:
        stmt = select(Dataset).options(
            selectinload(Dataset.statistics),
            selectinload(Dataset.feature_catalog)
        ).where(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id,
            Dataset.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_sha256_and_user(self, sha256: str, user_id: Any) -> Optional[Dataset]:
        stmt = select(Dataset).options(selectinload(Dataset.statistics)).where(
            Dataset.sha256_checksum == sha256,
            Dataset.user_id == user_id,
            Dataset.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_datasets_paginated(
        self,
        user_id: Any,
        project_id: Optional[Any] = None,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        stage: Optional[DatasetStage] = None,
        status: Optional[DatasetStatus] = None,
        is_latest: Optional[bool] = None,
        sort_by: str = "uploaded_at",
        sort_desc: bool = True,
    ) -> Tuple[List[Dataset], int]:
        filters = [Dataset.user_id == user_id, Dataset.is_deleted == False]
        
        if project_id is not None:
            filters.append(Dataset.project_id == project_id)
            
        if stage is not None:
            filters.append(Dataset.dataset_stage == stage)
            
        if status is not None:
            filters.append(Dataset.status == status)
            
        if is_latest is not None:
            filters.append(Dataset.is_latest == is_latest)
            
        if search:
            filters.append(
                or_(
                    Dataset.name.ilike(f"%{search}%"),
                    Dataset.description.ilike(f"%{search}%"),
                    Dataset.original_filename.ilike(f"%{search}%")
                )
            )
            
        count_stmt = select(func.count()).select_from(Dataset).where(and_(*filters))
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar() or 0
        
        stmt = select(Dataset).options(selectinload(Dataset.statistics)).where(and_(*filters))
        
        sort_col = getattr(Dataset, sort_by, Dataset.uploaded_at)
        if sort_desc:
            stmt = stmt.order_by(sort_col.desc())
        else:
            stmt = stmt.order_by(sort_col.asc())
            
        offset_val = (page - 1) * page_size
        stmt = stmt.offset(offset_val).limit(page_size)
        
        result = await self.session.execute(stmt)
        datasets = list(result.scalars().all())
        
        return datasets, total_count
