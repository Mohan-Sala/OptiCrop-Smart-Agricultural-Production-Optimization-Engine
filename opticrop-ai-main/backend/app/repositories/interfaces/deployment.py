from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict
from datetime import datetime
from app.models.deployment import (
    DeploymentEnvironment,
    DeploymentSetting,
    DeploymentPolicy,
    ModelDeployment,
    DeploymentManifestHistory,
    DeploymentEnvironmentVariable,
    DeploymentVersion,
    DeploymentJobLock,
    DeploymentApproval,
    DeploymentHealthLog,
    DeploymentEvent,
    DeploymentReplayMetric,
    DeploymentTag,
    DeploymentEventCheckpoint,
    DeploymentFreezeWindow,
)

class DeploymentRepository(ABC):
    """Abstract interface for managing MLOps deployment registry entities."""

    # Environments
    @abstractmethod
    async def create_environment(self, env: DeploymentEnvironment) -> DeploymentEnvironment:
        pass

    @abstractmethod
    async def get_environment(self, id: Any) -> Optional[DeploymentEnvironment]:
        pass

    @abstractmethod
    async def list_environments(self, project_id: Any) -> List[DeploymentEnvironment]:
        pass

    # Settings
    @abstractmethod
    async def get_settings(self, project_id: Any) -> Optional[DeploymentSetting]:
        pass

    @abstractmethod
    async def save_settings(self, settings: DeploymentSetting) -> DeploymentSetting:
        pass

    # Policies
    @abstractmethod
    async def create_policy(self, policy: DeploymentPolicy) -> DeploymentPolicy:
        pass

    @abstractmethod
    async def get_policy(self, id: Any) -> Optional[DeploymentPolicy]:
        pass

    @abstractmethod
    async def get_active_policy(self, project_id: Any) -> Optional[DeploymentPolicy]:
        pass

    # Deployments
    @abstractmethod
    async def create_deployment(self, deployment: ModelDeployment) -> ModelDeployment:
        pass

    @abstractmethod
    async def get_deployment(self, id: Any) -> Optional[ModelDeployment]:
        pass

    @abstractmethod
    async def update_deployment(self, deployment: ModelDeployment) -> ModelDeployment:
        pass

    @abstractmethod
    async def get_by_idempotency_key(self, user_id: Any, key: str) -> Optional[ModelDeployment]:
        pass

    @abstractmethod
    async def list_deployments(self, project_id: Any, status: Optional[str] = None, tag_key: Optional[str] = None, tag_value: Optional[str] = None) -> List[ModelDeployment]:
        pass

    # Manifest History
    @abstractmethod
    async def create_manifest_history(self, history: DeploymentManifestHistory) -> DeploymentManifestHistory:
        pass

    @abstractmethod
    async def get_manifest_history(self, deployment_id: Any) -> List[DeploymentManifestHistory]:
        pass

    # Checkpoints
    @abstractmethod
    async def create_checkpoint(self, checkpoint: DeploymentEventCheckpoint) -> DeploymentEventCheckpoint:
        pass

    @abstractmethod
    async def get_latest_checkpoint(self, deployment_id: Any) -> Optional[DeploymentEventCheckpoint]:
        pass

    # Events (Event Sourcing Audit)
    @abstractmethod
    async def create_event(self, event: DeploymentEvent) -> DeploymentEvent:
        pass

    @abstractmethod
    async def get_events(self, deployment_id: Any) -> List[DeploymentEvent]:
        pass

    @abstractmethod
    async def get_latest_event(self, deployment_id: Any) -> Optional[DeploymentEvent]:
        pass

    # Replay Metrics
    @abstractmethod
    async def create_replay_metric(self, metric: DeploymentReplayMetric) -> DeploymentReplayMetric:
        pass

    @abstractmethod
    async def list_replay_metrics(self, deployment_id: Any) -> List[DeploymentReplayMetric]:
        pass

    # Tags
    @abstractmethod
    async def create_tag(self, tag: DeploymentTag) -> DeploymentTag:
        pass

    @abstractmethod
    async def get_tags(self, deployment_id: Any) -> List[DeploymentTag]:
        pass

    # Approvals
    @abstractmethod
    async def create_approval(self, approval: DeploymentApproval) -> DeploymentApproval:
        pass

    @abstractmethod
    async def get_approval(self, id: Any) -> Optional[DeploymentApproval]:
        pass

    @abstractmethod
    async def update_approval(self, approval: DeploymentApproval) -> DeploymentApproval:
        pass

    @abstractmethod
    async def get_approvals(self, deployment_id: Any) -> List[DeploymentApproval]:
        pass

    # Versions
    @abstractmethod
    async def create_version(self, version: DeploymentVersion) -> DeploymentVersion:
        pass

    @abstractmethod
    async def get_versions(self, deployment_id: Any) -> List[DeploymentVersion]:
        pass

    # Environment Variables
    @abstractmethod
    async def create_variable(self, variable: DeploymentEnvironmentVariable) -> DeploymentEnvironmentVariable:
        pass

    @abstractmethod
    async def get_variables(self, deployment_id: Any) -> List[DeploymentEnvironmentVariable]:
        pass

    # Job Locks
    @abstractmethod
    async def acquire_lock(self, lock: DeploymentJobLock) -> bool:
        pass

    @abstractmethod
    async def release_lock(self, environment_id: Any, lease_owner: Any) -> bool:
        pass

    @abstractmethod
    async def heartbeat_lock(self, environment_id: Any, lease_owner: Any, duration_seconds: int) -> bool:
        pass

    @abstractmethod
    async def get_lock(self, environment_id: Any) -> Optional[DeploymentJobLock]:
        pass

    @abstractmethod
    async def list_expired_locks(self) -> List[DeploymentJobLock]:
        pass

    # Health & Telemetry Logs
    @abstractmethod
    async def create_health_log(self, log: DeploymentHealthLog) -> DeploymentHealthLog:
        pass

    @abstractmethod
    async def get_health_logs(self, deployment_id: Any, limit: int = 100) -> List[DeploymentHealthLog]:
        pass

    @abstractmethod
    async def get_health_aggregates(self, deployment_id: Any) -> Dict[str, Any]:
        pass

    # Freeze Windows
    @abstractmethod
    async def create_freeze_window(self, window: DeploymentFreezeWindow) -> DeploymentFreezeWindow:
        pass

    @abstractmethod
    async def list_freeze_windows(self, project_id: Any) -> List[DeploymentFreezeWindow]:
        pass
