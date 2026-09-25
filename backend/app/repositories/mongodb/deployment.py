import uuid
from typing import Any, List, Optional, Dict
from datetime import datetime, timezone
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
from app.models.trained_model import TrainedModel
from app.repositories.interfaces.deployment import DeploymentRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoDeploymentRepository(MongoBaseRepository[ModelDeployment], DeploymentRepository):
    """Concrete MongoDB / Beanie implementation of DeploymentRepository."""

    def __init__(self, *args, **kwargs):
        super().__init__(ModelDeployment, *args, **kwargs)

    # Environments
    async def create_environment(self, env: DeploymentEnvironment) -> DeploymentEnvironment:
        await env.insert()
        return env

    async def get_environment(self, id: Any) -> Optional[DeploymentEnvironment]:
        parsed_id = to_uuid(id)
        env = await DeploymentEnvironment.get(parsed_id)
        if not env and parsed_id != id:
            env = await DeploymentEnvironment.get(id)
        return env

    async def list_environments(self, project_id: Any) -> List[DeploymentEnvironment]:
        return await DeploymentEnvironment.find(
            DeploymentEnvironment.project_id == to_uuid(project_id)
        ).to_list()

    # Settings
    async def get_settings(self, project_id: Any) -> Optional[DeploymentSetting]:
        return await DeploymentSetting.find_one(
            DeploymentSetting.project_id == to_uuid(project_id)
        )

    async def save_settings(self, settings: DeploymentSetting) -> DeploymentSetting:
        parsed_project_id = to_uuid(settings.project_id)
        existing = await DeploymentSetting.find_one(
            DeploymentSetting.project_id == parsed_project_id
        )
        if existing:
            existing.checkpoint_interval = settings.checkpoint_interval
            existing.checkpoint_retention_days = settings.checkpoint_retention_days
            await existing.save()
            return existing
        else:
            await settings.insert()
            return settings

    # Policies
    async def create_policy(self, policy: DeploymentPolicy) -> DeploymentPolicy:
        await policy.insert()
        return policy

    async def get_policy(self, id: Any) -> Optional[DeploymentPolicy]:
        parsed_id = to_uuid(id)
        policy = await DeploymentPolicy.get(parsed_id)
        if not policy and parsed_id != id:
            policy = await DeploymentPolicy.get(id)
        return policy

    async def get_active_policy(self, project_id: Any) -> Optional[DeploymentPolicy]:
        return await DeploymentPolicy.find_one(
            DeploymentPolicy.project_id == to_uuid(project_id),
            DeploymentPolicy.is_active == True,
            sort=[("-policy_version", 1)],
        )

    # Deployments
    async def _populate_deployment_relations(self, deployment: Optional[ModelDeployment]) -> Optional[ModelDeployment]:
        if not deployment:
            return None
        if hasattr(deployment, "environment_id") and deployment.environment_id:
            deployment.environment = await DeploymentEnvironment.get(deployment.environment_id)
        if hasattr(deployment, "policy_version_id") and deployment.policy_version_id:
            deployment.policy_version = await DeploymentPolicy.get(deployment.policy_version_id)
        if hasattr(deployment, "model_id") and deployment.model_id:
            deployment.model = await TrainedModel.get(deployment.model_id)
        return deployment

    async def create_deployment(self, deployment: ModelDeployment) -> ModelDeployment:
        await deployment.insert()
        return await self._populate_deployment_relations(deployment)

    async def get_deployment(self, id: Any) -> Optional[ModelDeployment]:
        parsed_id = to_uuid(id)
        deployment = await ModelDeployment.get(parsed_id)
        if not deployment and parsed_id != id:
            deployment = await ModelDeployment.get(id)
        return await self._populate_deployment_relations(deployment)

    async def update_deployment(self, deployment: ModelDeployment) -> ModelDeployment:
        deployment.version_number += 1
        deployment.updated_at = datetime.now(timezone.utc)
        await deployment.save()
        return await self._populate_deployment_relations(deployment)

    async def get_by_idempotency_key(self, user_id: Any, key: str) -> Optional[ModelDeployment]:
        deployment = await ModelDeployment.find_one(
            ModelDeployment.created_by == to_uuid(user_id),
            ModelDeployment.idempotency_key == key,
        )
        return await self._populate_deployment_relations(deployment)

    async def list_deployments(
        self,
        project_id: Any,
        status: Optional[str] = None,
        tag_key: Optional[str] = None,
        tag_value: Optional[str] = None,
    ) -> List[ModelDeployment]:
        query: dict = {"project_id": to_uuid(project_id)}
        if status:
            query["status"] = status

        if tag_key or tag_value:
            tag_query: dict = {}
            if tag_key:
                tag_query["key"] = tag_key
            if tag_value:
                tag_query["value"] = tag_value
            tags = await DeploymentTag.find(tag_query).to_list()
            matched_deployment_ids = [t.deployment_id for t in tags]
            query["_id"] = {"$in": matched_deployment_ids}

        deployments = await ModelDeployment.find(query).sort("-created_at").to_list()
        for d in deployments:
            await self._populate_deployment_relations(d)
        return deployments

    # Manifest History
    async def create_manifest_history(self, history: DeploymentManifestHistory) -> DeploymentManifestHistory:
        await history.insert()
        return history

    async def get_manifest_history(self, deployment_id: Any) -> List[DeploymentManifestHistory]:
        return await DeploymentManifestHistory.find(
            DeploymentManifestHistory.deployment_id == to_uuid(deployment_id)
        ).sort("-generated_at").to_list()

    # Checkpoints
    async def create_checkpoint(self, checkpoint: DeploymentEventCheckpoint) -> DeploymentEventCheckpoint:
        await checkpoint.insert()
        return checkpoint

    async def get_latest_checkpoint(self, deployment_id: Any) -> Optional[DeploymentEventCheckpoint]:
        return await DeploymentEventCheckpoint.find_one(
            DeploymentEventCheckpoint.deployment_id == to_uuid(deployment_id),
            sort=[("-last_sequence_number", 1)],
        )

    # Events (Event Sourcing Audit)
    async def create_event(self, event: DeploymentEvent) -> DeploymentEvent:
        await event.insert()
        return event

    async def get_events(self, deployment_id: Any) -> List[DeploymentEvent]:
        return await DeploymentEvent.find(
            DeploymentEvent.deployment_id == to_uuid(deployment_id)
        ).sort("+sequence_number").to_list()

    async def get_latest_event(self, deployment_id: Any) -> Optional[DeploymentEvent]:
        return await DeploymentEvent.find_one(
            DeploymentEvent.deployment_id == to_uuid(deployment_id),
            sort=[("-sequence_number", 1)],
        )

    # Replay Metrics
    async def create_replay_metric(self, metric: DeploymentReplayMetric) -> DeploymentReplayMetric:
        await metric.insert()
        return metric

    async def list_replay_metrics(self, deployment_id: Any) -> List[DeploymentReplayMetric]:
        return await DeploymentReplayMetric.find(
            DeploymentReplayMetric.deployment_id == to_uuid(deployment_id)
        ).sort("-created_at").to_list()

    # Tags
    async def create_tag(self, tag: DeploymentTag) -> DeploymentTag:
        await tag.insert()
        return tag

    async def get_tags(self, deployment_id: Any) -> List[DeploymentTag]:
        return await DeploymentTag.find(
            DeploymentTag.deployment_id == to_uuid(deployment_id)
        ).to_list()

    # Approvals
    async def create_approval(self, approval: DeploymentApproval) -> DeploymentApproval:
        await approval.insert()
        return approval

    async def get_approval(self, id: Any) -> Optional[DeploymentApproval]:
        parsed_id = to_uuid(id)
        appr = await DeploymentApproval.get(parsed_id)
        if not appr and parsed_id != id:
            appr = await DeploymentApproval.get(id)
        return appr

    async def update_approval(self, approval: DeploymentApproval) -> DeploymentApproval:
        approval.updated_at = datetime.now(timezone.utc)
        await approval.save()
        return approval

    async def get_approvals(self, deployment_id: Any) -> List[DeploymentApproval]:
        return await DeploymentApproval.find(
            DeploymentApproval.deployment_id == to_uuid(deployment_id)
        ).sort("+reviewer_order").to_list()

    # Versions
    async def create_version(self, version: DeploymentVersion) -> DeploymentVersion:
        await version.insert()
        return version

    async def get_versions(self, deployment_id: Any) -> List[DeploymentVersion]:
        return await DeploymentVersion.find(
            DeploymentVersion.deployment_id == to_uuid(deployment_id)
        ).sort("-version_number").to_list()

    # Environment Variables
    async def create_variable(self, variable: DeploymentEnvironmentVariable) -> DeploymentEnvironmentVariable:
        await variable.insert()
        return variable

    async def get_variables(self, deployment_id: Any) -> List[DeploymentEnvironmentVariable]:
        return await DeploymentEnvironmentVariable.find(
            DeploymentEnvironmentVariable.deployment_id == to_uuid(deployment_id)
        ).to_list()

    # Job Locks
    async def acquire_lock(self, lock: DeploymentJobLock) -> bool:
        parsed_env_id = to_uuid(lock.environment_id)
        now_dt = datetime.now(timezone.utc)
        existing = await DeploymentJobLock.find_one(
            DeploymentJobLock.environment_id == parsed_env_id
        )
        if existing:
            if existing.expires_at < now_dt or existing.lease_owner == lock.lease_owner:
                existing.lease_owner = lock.lease_owner
                existing.acquired_at = lock.acquired_at
                existing.heartbeat_at = lock.heartbeat_at
                existing.expires_at = lock.expires_at
                await existing.save()
                return True
            return False
        else:
            await lock.insert()
            return True

    async def release_lock(self, environment_id: Any, lease_owner: Any) -> bool:
        result = await DeploymentJobLock.find({
            "environment_id": to_uuid(environment_id),
            "lease_owner": to_uuid(lease_owner),
        }).delete()
        return result.deleted_count > 0

    async def heartbeat_lock(self, environment_id: Any, lease_owner: Any, duration_seconds: int) -> bool:
        existing = await DeploymentJobLock.find_one({
            "environment_id": to_uuid(environment_id),
            "lease_owner": to_uuid(lease_owner),
        })
        if existing:
            now_dt = datetime.now(timezone.utc)
            existing.heartbeat_at = now_dt
            existing.expires_at = datetime.fromtimestamp(now_dt.timestamp() + duration_seconds, tz=timezone.utc)
            await existing.save()
            return True
        return False

    async def get_lock(self, environment_id: Any) -> Optional[DeploymentJobLock]:
        return await DeploymentJobLock.find_one(
            DeploymentJobLock.environment_id == to_uuid(environment_id)
        )

    async def list_expired_locks(self) -> List[DeploymentJobLock]:
        now_dt = datetime.now(timezone.utc)
        return await DeploymentJobLock.find(
            DeploymentJobLock.expires_at < now_dt
        ).to_list()

    # Health & Telemetry Logs
    async def create_health_log(self, log: DeploymentHealthLog) -> DeploymentHealthLog:
        await log.insert()
        return log

    async def get_health_logs(self, deployment_id: Any, limit: int = 100) -> List[DeploymentHealthLog]:
        return await DeploymentHealthLog.find(
            DeploymentHealthLog.deployment_id == to_uuid(deployment_id)
        ).sort("-recorded_at").limit(limit).to_list()

    async def get_health_aggregates(self, deployment_id: Any) -> Dict[str, Any]:
        logs = await DeploymentHealthLog.find(
            DeploymentHealthLog.deployment_id == to_uuid(deployment_id)
        ).to_list()

        if not logs:
            return {
                "avg_cpu": 0.0,
                "avg_memory": 0.0,
                "avg_latency": 0.0,
                "avg_throughput": 0.0,
                "total_errors": 0,
                "unhealthy_count": 0,
            }

        count = len(logs)
        return {
            "avg_cpu": float(sum(l.cpu_usage_pct for l in logs) / count),
            "avg_memory": float(sum(l.memory_usage_mb for l in logs) / count),
            "avg_latency": float(sum(l.latency_ms for l in logs) / count),
            "avg_throughput": float(sum(l.throughput_rps for l in logs) / count),
            "total_errors": int(sum(l.error_count for l in logs)),
            "unhealthy_count": int(sum(1 for l in logs if l.status == "UNHEALTHY")),
        }

    # Freeze Windows
    async def create_freeze_window(self, window: DeploymentFreezeWindow) -> DeploymentFreezeWindow:
        await window.insert()
        return window

    async def list_freeze_windows(self, project_id: Any) -> List[DeploymentFreezeWindow]:
        return await DeploymentFreezeWindow.find(
            DeploymentFreezeWindow.project_id == to_uuid(project_id)
        ).to_list()
