import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, BackgroundTasks, status

from app.dependencies.auth import get_active_user
from app.dependencies.dataset import get_dataset_repository, get_project_repository
from app.dependencies.preprocessing import get_preprocessing_repository, get_preprocessing_pipeline
from app.schemas.preprocessing import (
    PreprocessingConfigRequest,
    PreprocessingRunResponse,
    PreprocessingRunDetailsResponse,
    PreprocessingHistoryResponse,
)
from app.utils.exceptions import NotFoundException, AuthorizationException

router = APIRouter()


@router.post("/", response_model=PreprocessingRunResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_preprocessing(
    background_tasks: BackgroundTasks,
    dataset_id: uuid.UUID,
    project_id: uuid.UUID,
    payload: PreprocessingConfigRequest,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    dataset_repo=Depends(get_dataset_repository),
    pipeline=Depends(get_preprocessing_pipeline),
):
    """Triggers ML Preprocessing pipeline in the background.

    Performs security checks and returns HTTP 202 status.
    """
    # 1. Verify project ownership
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found or access denied.")

    # 2. Verify dataset ownership
    dataset = await dataset_repo.get_by_id_and_user_id(dataset_id, current_user.id)
    if not dataset:
        raise NotFoundException("Dataset not found or access denied.")

    return await pipeline.initiate_run(
        dataset_id=dataset_id,
        project_id=project_id,
        user_id=current_user.id,
        config=payload.model_dump(),
        background_tasks=background_tasks,
    )


@router.get("/{preprocessing_id}", response_model=PreprocessingRunDetailsResponse)
async def get_preprocessing_details(
    preprocessing_id: uuid.UUID,
    current_user=Depends(get_active_user),
    prep_repo=Depends(get_preprocessing_repository),
):
    """Retrieves parameters and execution status for a single preprocessing run."""
    run = await prep_repo.get_by_id(preprocessing_id)
    if not run or run.user_id != current_user.id:
        raise NotFoundException("Preprocessing run not found or access denied.")
    return run


@router.get("/{preprocessing_id}/report")
async def get_preprocessing_report(
    preprocessing_id: uuid.UUID,
    current_user=Depends(get_active_user),
    prep_repo=Depends(get_preprocessing_repository),
):
    """Retrieves the generated report statistics for a completed run."""
    run = await prep_repo.get_by_id(preprocessing_id)
    if not run or run.user_id != current_user.id:
        raise NotFoundException("Preprocessing run not found or access denied.")
    if run.status != "COMPLETED":
        raise NotFoundException("Report is not available: preprocessing is not completed.")
    return run.report


@router.get("/{dataset_id}/history", response_model=PreprocessingHistoryResponse)
async def get_preprocessing_history(
    dataset_id: uuid.UUID,
    current_user=Depends(get_active_user),
    dataset_repo=Depends(get_dataset_repository),
    prep_repo=Depends(get_preprocessing_repository),
):
    """Lists historical preprocessing runs mapping to a target dataset version."""
    dataset = await dataset_repo.get_by_id_and_user_id(dataset_id, current_user.id)
    if not dataset:
        raise NotFoundException("Dataset not found or access denied.")

    runs = await prep_repo.get_by_dataset_id(dataset_id)
    return PreprocessingHistoryResponse(items=runs, total=len(runs))
