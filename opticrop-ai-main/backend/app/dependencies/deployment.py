from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.interfaces.deployment import DeploymentRepository
from app.repositories.sqlalchemy.deployment import SqlAlchemyDeploymentRepository
from app.services.deployment.checkpoints import CheckpointManager
from app.services.deployment.orchestrator import DeploymentOrchestrator
from app.services.deployment.scheduler import DeploymentSchedulerService

def get_deployment_repository(db: AsyncSession = Depends(get_db)) -> DeploymentRepository:
    return SqlAlchemyDeploymentRepository(db)


def get_checkpoint_manager(
    repo: DeploymentRepository = Depends(get_deployment_repository)
) -> CheckpointManager:
    return CheckpointManager(repo)


def get_deployment_orchestrator(
    repo: DeploymentRepository = Depends(get_deployment_repository),
    checkpoint_mgr: CheckpointManager = Depends(get_checkpoint_manager)
) -> DeploymentOrchestrator:
    return DeploymentOrchestrator(repo, checkpoint_mgr)


def get_deployment_scheduler_service(
    repo: DeploymentRepository = Depends(get_deployment_repository)
) -> DeploymentSchedulerService:
    return DeploymentSchedulerService(repo)
