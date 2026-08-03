import anyio
import os
import shutil
import uuid
import logging
from datetime import datetime, timezone
from typing import Any, List, Optional, Tuple
from fastapi import UploadFile, BackgroundTasks

from app.core.config import settings
from app.core.enums import DatasetStatus, DatasetStage
from app.models.dataset import Dataset
from app.models.dataset_statistics import DatasetStatistics
from app.repositories.interfaces.dataset import DatasetRepository
from app.services.dataset.validation import ValidationService
from app.services.dataset.storage import StorageService
from app.services.dataset.metadata import MetadataService
from app.services.dataset.preview import PreviewService
from app.utils.exceptions import ValidationException, NotFoundException, ConflictException

logger = logging.getLogger("app.services.dataset")


class DatasetService:
    """Orchestrates dataset uploads, validation, profiling statistics, updates, and storage lifecycles."""

    def __init__(
        self,
        dataset_repo: DatasetRepository,
        validation_service: ValidationService,
        storage_service: StorageService,
        metadata_service: MetadataService,
        preview_service: PreviewService,
    ):
        self.dataset_repo = dataset_repo
        self.validation_service = validation_service
        self.storage_service = storage_service
        self.metadata_service = metadata_service
        self.preview_service = preview_service

    async def initiate_upload(
        self,
        file: UploadFile,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        background_tasks: BackgroundTasks,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dataset:
        """Initiates the upload pipeline, streaming the file to temporary storage and triggering background jobs."""
        filename = file.filename or "dataset.csv"
        content_type = file.content_type or "text/csv"

        # 1. Stream file to local temporary path to retrieve exact size
        os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
        temp_file_id = uuid.uuid4()
        temp_file_path = os.path.join(settings.UPLOAD_PATH, f"{temp_file_id}.csv")

        try:
            file_size = 0
            with open(temp_file_path, "wb") as f:
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    file_size += len(chunk)
                    f.write(chunk)
            
            # 2. Perform basic file metadata checks
            self.validation_service.validate_file_basics(filename, content_type, file_size)

            # 3. Calculate SHA-256 and check for duplicates to prevent redundant file storage
            sha256 = await self.metadata_service.calculate_sha256(temp_file_path)
            existing = await self.dataset_repo.get_by_sha256_and_user(sha256, user_id)
            if existing:
                raise ConflictException(
                    f"A duplicate dataset with the same checksum already exists (ID: {existing.id}, Name: {existing.name})."
                )

            # 4. Construct unique storage filename
            dataset_id = uuid.uuid4()
            stored_filename = f"{dataset_id}_v1.csv"
            storage_path = f"{user_id}/{project_id}/{stored_filename}"

            # 5. Create initial pending database record
            dataset_record = Dataset(
                id=dataset_id,
                project_id=project_id,
                user_id=user_id,
                name=filename.rsplit(".", 1)[0],
                original_filename=filename,
                stored_filename=stored_filename,
                storage_path=storage_path,
                version=1,
                is_latest=True,
                dataset_stage=DatasetStage.RAW,
                status=DatasetStatus.UPLOADING,
                size=file_size,
                description=description,
                tags=tags,
                sha256_checksum=sha256,
            )
            created_record = await self.dataset_repo.create(dataset_record)
            await self.dataset_repo.session.commit()

            # 6. Schedule long-running background parsing/uploads in worker pool
            background_tasks.add_task(
                self.process_dataset_upload,
                dataset_id,
                temp_file_path,
                user_id,
                project_id,
                content_type,
            )

            return created_record

        except Exception as e:
            # Clean up temp file immediately if validation or DB insert fails
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise e

    async def process_dataset_upload(
        self,
        dataset_id: uuid.UUID,
        temp_file_path: str,
        user_id: uuid.UUID,
        project_id: uuid.UUID,
        content_type: str,
    ) -> None:
        """Background worker task verifying structures, extracting profiles, uploading, and updating database state."""
        try:
            logger.info("Processing background upload for dataset ID: %s", dataset_id)
            
            # Isolated import inside background execution block to prevent dependency loop/thread collisions
            from app.database.session import async_session
            from app.repositories.sqlalchemy.dataset import SqlAlchemyDatasetRepository

            async with async_session() as session:
                dataset_repo = SqlAlchemyDatasetRepository(session)
                dataset = await dataset_repo.get_by_id(dataset_id)
                if not dataset:
                    logger.error("Dataset record %s not found in database.", dataset_id)
                    return
                
                dataset.status = DatasetStatus.VALIDATING
                await session.flush()
                await session.commit()

            # Detect encoding and delimiter
            encoding, delimiter = await self.metadata_service.detect_encoding_and_delimiter(temp_file_path)

            # Validate CSV content
            await anyio.to_thread.run_sync(
                self.validation_service.validate_csv_content,
                temp_file_path,
                encoding,
                delimiter
            )

            # Calculate profiling statistics
            stats_data = await self.preview_service.calculate_statistics(temp_file_path, delimiter, encoding)

            # Extract dimensions
            shape_info = await self.preview_service.generate_preview(temp_file_path, delimiter, encoding)
            rows = shape_info["shape"][0]
            cols = shape_info["shape"][1]

            # Upload verified CSV file to Supabase storage bucket
            storage_path = f"{user_id}/{project_id}/{dataset.stored_filename}"
            await self.storage_service.upload_file(storage_path, temp_file_path, content_type)

            # Save statistics and flag state as VALIDATED
            async with async_session() as session:
                dataset_repo = SqlAlchemyDatasetRepository(session)
                dataset = await dataset_repo.get_by_id(dataset_id)
                if dataset:
                    dataset.status = DatasetStatus.VALIDATED
                    dataset.rows = rows
                    dataset.columns = cols
                    dataset.delimiter = delimiter
                    dataset.encoding = encoding
                    dataset.storage_path = storage_path
                    
                    # Create stats profile record
                    stats_record = DatasetStatistics(
                        dataset_id=dataset_id,
                        missing_values=stats_data["missing_values"],
                        duplicate_rows=stats_data["duplicate_rows"],
                        duplicate_columns=stats_data["duplicate_columns"],
                        memory_usage=stats_data["memory_usage"],
                        column_summary=stats_data["column_summary"]
                    )
                    session.add(stats_record)
                    await session.flush()
                    await session.commit()

            logger.info("Successfully completed processing for dataset ID: %s", dataset_id)

        except Exception as e:
            logger.error("Background task failed for dataset ID: %s. Error: %s", dataset_id, str(e), exc_info=True)
            from app.database.session import async_session
            from app.repositories.sqlalchemy.dataset import SqlAlchemyDatasetRepository
            
            async with async_session() as session:
                dataset_repo = SqlAlchemyDatasetRepository(session)
                dataset = await dataset_repo.get_by_id(dataset_id)
                if dataset:
                    dataset.status = DatasetStatus.FAILED
                    await session.flush()
                    await session.commit()
        finally:
            # Clean up temp file safely
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as cleanup_err:
                    logger.warning("Failed to remove temp file %s: %s", temp_file_path, str(cleanup_err))

    async def list_datasets(
        self,
        user_id: uuid.UUID,
        project_id: Optional[uuid.UUID] = None,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        stage: Optional[DatasetStage] = None,
        status: Optional[DatasetStatus] = None,
        is_latest: Optional[bool] = None,
        sort_by: str = "uploaded_at",
        sort_desc: bool = True,
    ) -> Tuple[List[Dataset], int]:
        """Fetches active dataset listings bound to user queries and pagination filters."""
        return await self.dataset_repo.list_datasets_paginated(
            user_id=user_id,
            project_id=project_id,
            page=page,
            page_size=page_size,
            search=search,
            stage=stage,
            status=status,
            is_latest=is_latest,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )

    async def get_dataset_details(self, dataset_id: uuid.UUID, user_id: uuid.UUID) -> Dataset:
        """Retrieves details of a dataset, including statistics if available."""
        dataset = await self.dataset_repo.get_by_id_and_user_id(dataset_id, user_id)
        if not dataset:
            raise NotFoundException("Dataset not found or access denied.")
        return dataset

    async def get_dataset_preview(self, dataset_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """Generates preview sample rows and metadata schema."""
        dataset = await self.get_dataset_details(dataset_id, user_id)
        if dataset.status != DatasetStatus.VALIDATED:
            raise ValidationException(
                f"Cannot generate preview: dataset is in state '{dataset.status}' and not yet fully validated."
            )

        # 1. Download file content temporarily to parse preview
        temp_file_path = os.path.join(settings.UPLOAD_PATH, f"preview_{uuid.uuid4()}.csv")
        try:
            file_bytes = await self.storage_service.download_file(dataset.storage_path)
            with open(temp_file_path, "wb") as f:
                f.write(file_bytes)
            
            # 2. Extract preview columns and statistics
            preview = await self.preview_service.generate_preview(
                temp_file_path,
                dataset.delimiter or ",",
                dataset.encoding or "utf-8"
            )
            preview["dataset_id"] = dataset_id
            return preview

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    async def download_dataset(self, dataset_id: uuid.UUID, user_id: uuid.UUID) -> Tuple[bytes, str]:
        """Retrieves raw CSV file bytes for secure downloads."""
        dataset = await self.get_dataset_details(dataset_id, user_id)
        if dataset.status != DatasetStatus.VALIDATED:
            raise ValidationException(
                f"Cannot download file: dataset is in state '{dataset.status}' and not yet fully validated."
            )
            
        file_bytes = await self.storage_service.download_file(dataset.storage_path)
        return file_bytes, dataset.original_filename

    async def rename_dataset(
        self,
        dataset_id: uuid.UUID,
        user_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dataset:
        """Modifies name, description, and tags metadata for a dataset."""
        dataset = await self.get_dataset_details(dataset_id, user_id)
        
        # Enforce check on locked status
        if dataset.is_locked or dataset.locked_by_training:
            raise ConflictException("Cannot rename dataset: resource is locked by active tasks.")

        update_fields = {"name": name, "description": description, "tags": tags}
        updated_dataset = await self.dataset_repo.update(dataset_id, update_fields)
        await self.dataset_repo.save()
        return updated_dataset

    async def delete_dataset(self, dataset_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Performs soft-delete in PostgreSQL and cleans up Supabase Storage files safely."""
        dataset = await self.get_dataset_details(dataset_id, user_id)

        # Enforce locks verification
        if dataset.is_locked or dataset.locked_by_training:
            raise ConflictException("Cannot delete dataset: resource is locked and actively used in training runs.")

        # 1. Flag database record as soft-deleted
        soft_delete_fields = {
            "is_deleted": True,
            "is_latest": False,
            "deleted_at": datetime.now(timezone.utc)
        }
        await self.dataset_repo.update(dataset_id, soft_delete_fields)
        await self.dataset_repo.save()

        # 2. Cleanup physical file inside Supabase bucket
        try:
            await self.storage_service.delete_file(dataset.storage_path)
        except Exception as storage_err:
            # Logs failure but does not crash, since metadata soft deletion successfully completed
            logger.error("Failed to clean up Supabase storage file %s: %s", dataset.storage_path, str(storage_err))
