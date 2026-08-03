from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.interfaces.dataset import DatasetRepository
from app.repositories.interfaces.project import ProjectRepository
from app.repositories.sqlalchemy.dataset import SqlAlchemyDatasetRepository
from app.repositories.sqlalchemy.project import SqlAlchemyProjectRepository
from app.services.dataset.validation import ValidationService
from app.services.dataset.storage import StorageService
from app.services.dataset.metadata import MetadataService
from app.services.dataset.preview import PreviewService
from app.services.dataset.service import DatasetService


def get_dataset_repository(db: AsyncSession = Depends(get_db)) -> DatasetRepository:
    return SqlAlchemyDatasetRepository(db)


def get_project_repository(db: AsyncSession = Depends(get_db)) -> ProjectRepository:
    return SqlAlchemyProjectRepository(db)


def get_validation_service() -> ValidationService:
    return ValidationService()


def get_storage_service() -> StorageService:
    return StorageService()


def get_metadata_service() -> MetadataService:
    return MetadataService()


def get_preview_service() -> PreviewService:
    return PreviewService()


def get_dataset_service(
    dataset_repo: DatasetRepository = Depends(get_dataset_repository),
    validation_service: ValidationService = Depends(get_validation_service),
    storage_service: StorageService = Depends(get_storage_service),
    metadata_service: MetadataService = Depends(get_metadata_service),
    preview_service: PreviewService = Depends(get_preview_service),
) -> DatasetService:
    return DatasetService(
        dataset_repo=dataset_repo,
        validation_service=validation_service,
        storage_service=storage_service,
        metadata_service=metadata_service,
        preview_service=preview_service,
    )
