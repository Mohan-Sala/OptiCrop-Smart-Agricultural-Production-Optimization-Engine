from fastapi import Depends

from app.repositories.interfaces.dataset import DatasetRepository
from app.repositories.interfaces.project import ProjectRepository
from app.repositories.mongodb.dataset import MongoDatasetRepository
from app.repositories.mongodb.project import MongoProjectRepository
from app.services.dataset.validation import ValidationService
from app.services.dataset.storage import StorageService
from app.services.dataset.metadata import MetadataService
from app.services.dataset.preview import PreviewService
from app.services.dataset.service import DatasetService


def get_dataset_repository() -> DatasetRepository:
    return MongoDatasetRepository()


def get_project_repository() -> ProjectRepository:
    return MongoProjectRepository()


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
        dataset_repo=dataset_repo if type(dataset_repo).__name__ != "Depends" else get_dataset_repository(),
        validation_service=validation_service if type(validation_service).__name__ != "Depends" else get_validation_service(),
        storage_service=storage_service if type(storage_service).__name__ != "Depends" else get_storage_service(),
        metadata_service=metadata_service if type(metadata_service).__name__ != "Depends" else get_metadata_service(),
        preview_service=preview_service if type(preview_service).__name__ != "Depends" else get_preview_service(),
    )
