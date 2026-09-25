from fastapi import Depends

from app.repositories.interfaces.deployment import DeploymentRepository
from app.repositories.mongodb.deployment import MongoDeploymentRepository
from app.services.deployment.checkpoints import CheckpointManager
from app.services.deployment.orchestrator import DeploymentOrchestrator
from app.services.deployment.scheduler import DeploymentSchedulerService

def get_deployment_repository() -> DeploymentRepository:
    return MongoDeploymentRepository()


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
