import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, BackgroundTasks, status

from app.dependencies.auth import get_active_user
from app.dependencies.dataset import get_dataset_repository, get_project_repository
from app.dependencies.training import (
    get_experiment_repository,
    get_training_session_repository,
    get_trained_model_repository,
    get_registry_service,
    get_training_pipeline,
)
from app.schemas.training import (
    ExperimentCreateRequest,
    ExperimentResponse,
    TrainingConfigRequest,
    TrainingSessionResponse,
    TrainedModelResponse,
    TrainedModelDetailsResponse,
)
from app.models.training_experiment import TrainingExperiment
from app.utils.exceptions import NotFoundException, ValidationException

router = APIRouter()


# --- 1. EXPERIMENT ENDPOINTS ---

@router.post("/experiments", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
async def create_experiment(
    payload: ExperimentCreateRequest,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    exp_repo=Depends(get_experiment_repository),
):
    """Creates a new ML Experiment category inside a project workspace."""
    project = await project_repo.get_by_id_and_user_id(payload.project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found or access denied.")

    experiment = TrainingExperiment(
        id=uuid.uuid4(),
        project_id=payload.project_id,
        name=payload.name,
        description=payload.description,
    )
    created = await exp_repo.create(experiment)
    await exp_repo.session.flush()
    await exp_repo.session.commit()
    return created


@router.get("/experiments", response_model=List[ExperimentResponse])
async def list_experiments(
    project_id: uuid.UUID,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    exp_repo=Depends(get_experiment_repository),
):
    """Lists all active experiments linked to a target project."""
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found or access denied.")

    return await exp_repo.get_by_project_id(project_id)


# --- 2. TRAINING RUN ENDPOINTS ---

@router.post("/", response_model=TrainingSessionResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_training_run(
    background_tasks: BackgroundTasks,
    dataset_id: uuid.UUID,
    project_id: uuid.UUID,
    payload: TrainingConfigRequest,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    dataset_repo=Depends(get_dataset_repository),
    pipeline=Depends(get_training_pipeline),
):
    """Triggers ML model training and parameter searches in the background."""
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found or access denied.")

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


@router.get("/sessions/{session_id}", response_model=TrainingSessionResponse)
async def get_training_session_details(
    session_id: uuid.UUID,
    current_user=Depends(get_active_user),
    session_repo=Depends(get_training_session_repository),
):
    """Retrieves execution parameter, run status, and winning model of a training run."""
    run = await session_repo.get_by_id(session_id)
    if not run or run.user_id != current_user.id:
        raise NotFoundException("Training session not found or access denied.")
    return run


@router.get("/sessions", response_model=List[TrainingSessionResponse])
async def list_training_sessions(
    project_id: uuid.UUID,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    session_repo=Depends(get_training_session_repository),
):
    """Lists historical training runs generated inside a project workspace."""
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found or access denied.")

    return await session_repo.get_by_project_id(project_id)


# --- 3. MODEL REGISTRY ENDPOINTS ---

@router.get("/models", response_model=List[TrainedModelResponse])
async def list_registered_models(
    project_id: uuid.UUID,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    registry=Depends(get_registry_service),
):
    """Lists registered models associated with a project."""
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found or access denied.")

    return await registry.list_models(project_id)


@router.get("/models/{model_id}", response_model=TrainedModelDetailsResponse)
async def get_registered_model_details(
    model_id: uuid.UUID,
    current_user=Depends(get_active_user),
    registry=Depends(get_registry_service),
):
    """Retrieves specifications, features signature, and evaluation reports of a model."""
    return await registry.get_model(model_id, current_user.id)


@router.post("/models/{model_id}/activate", response_model=TrainedModelResponse)
async def activate_registry_model(
    model_id: uuid.UUID,
    project_id: uuid.UUID,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    registry=Depends(get_registry_service),
):
    """Sets a model as active for live inference and automatically deactivates others."""
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found or access denied.")

    return await registry.activate_model(model_id, project_id, current_user.id)


@router.post("/models/{model_id}/archive", response_model=TrainedModelResponse)
async def archive_registry_model(
    model_id: uuid.UUID,
    current_user=Depends(get_active_user),
    registry=Depends(get_registry_service),
):
    """Changes model lifecycle state to ARCHIVED and deactivates it."""
    return await registry.archive_model(model_id, current_user.id)


@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registry_model(
    model_id: uuid.UUID,
    current_user=Depends(get_active_user),
    registry=Depends(get_registry_service),
):
    """Removes a model from the registry. Fails if the model is currently active."""
    await registry.delete_model(model_id, current_user.id)
