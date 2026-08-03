import io
import uuid
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, status, Request
from fastapi.responses import StreamingResponse

from app.dependencies.auth import get_active_user
from app.dependencies.dataset import get_dataset_service, get_project_repository
from app.core.enums import DatasetStatus, DatasetStage
from app.schemas.dataset import (
    DatasetResponse,
    DatasetDetailsResponse,
    DatasetListResponse,
    DatasetRenameRequest,
    DatasetPreviewResponse,
)
from app.utils.responses import success_response
from app.utils.exceptions import NotFoundException

router = APIRouter()


@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    project_id: uuid.UUID,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    dataset_service=Depends(get_dataset_service),
):
    """Initiates CSV upload under a project.

    Verifies project ownership and queues validation/profiling tasks.
    """
    # Verify target project belongs to current authenticated user
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found or access denied.")

    return await dataset_service.initiate_upload(
        file=file,
        project_id=project_id,
        user_id=current_user.id,
        background_tasks=background_tasks,
        description=description,
        tags=tags,
    )


@router.get("/", response_model=DatasetListResponse)
async def list_datasets(
    project_id: Optional[uuid.UUID] = None,
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    stage: Optional[DatasetStage] = None,
    status: Optional[DatasetStatus] = None,
    is_latest: Optional[bool] = None,
    sort_by: str = "uploaded_at",
    sort_desc: bool = True,
    current_user=Depends(get_active_user),
    dataset_service=Depends(get_dataset_service),
):
    """Lists non-deleted datasets with support for pagination, sorting, search, and stages."""
    datasets, total = await dataset_service.list_datasets(
        user_id=current_user.id,
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
    pages = math.ceil(total / page_size) if total > 0 else 1
    return DatasetListResponse(
        items=datasets,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{dataset_id}", response_model=DatasetDetailsResponse)
async def get_dataset_details(
    dataset_id: uuid.UUID,
    current_user=Depends(get_active_user),
    dataset_service=Depends(get_dataset_service),
):
    """Retrieves metadata of a single dataset and its profiling statistics."""
    return await dataset_service.get_dataset_details(dataset_id, current_user.id)


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
async def get_dataset_preview(
    dataset_id: uuid.UUID,
    current_user=Depends(get_active_user),
    dataset_service=Depends(get_dataset_service),
):
    """Generates preview columns, inferred data types, and first 10 rows."""
    return await dataset_service.get_dataset_preview(dataset_id, current_user.id)


@router.get("/{dataset_id}/download")
async def download_dataset(
    dataset_id: uuid.UUID,
    current_user=Depends(get_active_user),
    dataset_service=Depends(get_dataset_service),
):
    """Downloads raw CSV bytes securely."""
    file_bytes, filename = await dataset_service.download_dataset(dataset_id, current_user.id)
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.patch("/{dataset_id}", response_model=DatasetDetailsResponse)
async def rename_dataset(
    dataset_id: uuid.UUID,
    payload: DatasetRenameRequest,
    current_user=Depends(get_active_user),
    dataset_service=Depends(get_dataset_service),
):
    """Updates dataset name, description, or tags metadata."""
    return await dataset_service.rename_dataset(
        dataset_id=dataset_id,
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        tags=payload.tags,
    )


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: uuid.UUID,
    current_user=Depends(get_active_user),
    dataset_service=Depends(get_dataset_service),
):
    """Performs dataset soft-delete and storage file cleanup."""
    await dataset_service.delete_dataset(dataset_id, current_user.id)
    return success_response(message="Dataset deleted successfully.")
