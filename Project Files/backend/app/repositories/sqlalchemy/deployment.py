import uuid
from typing import Any, List, Optional, Dict
from datetime import datetime
from sqlalchemy import select, and_, or_, delete, update, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
from app.repositories.interfaces.deployment import DeploymentRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository

class SqlAlchemyDeploymentRepository(SqlAlchemyBaseRepository[ModelDeployment], DeploymentRepository):
    """Concrete SQLAlchemy implementation of DeploymentRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ModelDeployment)

    # Environments
    async def create_environment(self, env: DeploymentEnvironment) -> DeploymentEnvironment:
        self.session.add(env)
        await self.session.flush()
        await self.session.refresh(env)
        return env

    async def get_environment(self, id: Any) -> Optional[DeploymentEnvironment]:
        stmt = select(DeploymentEnvironment).where(DeploymentEnvironment.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_environments(self, project_id: Any) -> List[DeploymentEnvironment]:
        stmt = select(DeploymentEnvironment).where(DeploymentEnvironment.project_id == project_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Settings
    async def get_settings(self, project_id: Any) -> Optional[DeploymentSetting]:
        stmt = select(DeploymentSetting).where(DeploymentSetting.project_id == project_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def save_settings(self, settings: DeploymentSetting) -> DeploymentSetting:
        # Merge or add
        stmt = select(DeploymentSetting).where(DeploymentSetting.project_id == settings.project_id)
        res = await self.session.execute(stmt)
        existing = res.scalars().first()
        if existing:
            existing.checkpoint_interval = settings.checkpoint_interval
            existing.checkpoint_retention_days = settings.checkpoint_retention_days
            await self.session.flush()
            await self.session.refresh(existing)
            return existing
        else:
            self.session.add(settings)
            await self.session.flush()
            await self.session.refresh(settings)
            return settings

    # Policies
    async def create_policy(self, policy: DeploymentPolicy) -> DeploymentPolicy:
        self.session.add(policy)
        await self.session.flush()
        await self.session.refresh(policy)
        return policy

    async def get_policy(self, id: Any) -> Optional[DeploymentPolicy]:
        stmt = select(DeploymentPolicy).where(DeploymentPolicy.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_active_policy(self, project_id: Any) -> Optional[DeploymentPolicy]:
        stmt = select(DeploymentPolicy).where(
            and_(
                DeploymentPolicy.project_id == project_id,
                DeploymentPolicy.is_active == True
            )
        ).order_by(DeploymentPolicy.policy_version.desc())
        result = await self.session.execute(stmt)
        return result.scalars().first()

    # Deployments
    async def create_deployment(self, deployment: ModelDeployment) -> ModelDeployment:
        self.session.add(deployment)
        await self.session.flush()
        await self.session.refresh(deployment)
        return deployment

    async def get_deployment(self, id: Any) -> Optional[ModelDeployment]:
        stmt = (
            select(ModelDeployment)
            .options(
                selectinload(ModelDeployment.environment),
                selectinload(ModelDeployment.policy_version),
                selectinload(ModelDeployment.model)
            )
            .where(ModelDeployment.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_deployment(self, deployment: ModelDeployment) -> ModelDeployment:
        # Increment version_number for optimistic locking
        deployment.version_number += 1
        await self.session.flush()
        return await self.get_deployment(deployment.id)

    async def get_by_idempotency_key(self, user_id: Any, key: str) -> Optional[ModelDeployment]:
        stmt = select(ModelDeployment).where(
            and_(
                ModelDeployment.created_by == user_id,
                ModelDeployment.idempotency_key == key
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_deployments(self, project_id: Any, status: Optional[str] = None, tag_key: Optional[str] = None, tag_value: Optional[str] = None) -> List[ModelDeployment]:
        stmt = select(ModelDeployment).where(ModelDeployment.project_id == project_id)
        if status:
            stmt = stmt.where(ModelDeployment.status == status)
        if tag_key or tag_value:
            tag_filter = select(DeploymentTag.deployment_id)
            if tag_key:
                tag_filter = tag_filter.where(DeploymentTag.key == tag_key)
            if tag_value:
                tag_filter = tag_filter.where(DeploymentTag.value == tag_value)
            stmt = stmt.where(ModelDeployment.id.in_(tag_filter))
        stmt = stmt.order_by(ModelDeployment.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Manifest History
    async def create_manifest_history(self, history: DeploymentManifestHistory) -> DeploymentManifestHistory:
        self.session.add(history)
        await self.session.flush()
        await self.session.refresh(history)
        return history

    async def get_manifest_history(self, deployment_id: Any) -> List[DeploymentManifestHistory]:
        stmt = select(DeploymentManifestHistory).where(DeploymentManifestHistory.deployment_id == deployment_id).order_by(DeploymentManifestHistory.generated_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Checkpoints
    async def create_checkpoint(self, checkpoint: DeploymentEventCheckpoint) -> DeploymentEventCheckpoint:
        self.session.add(checkpoint)
        await self.session.flush()
        await self.session.refresh(checkpoint)
        return checkpoint

    async def get_latest_checkpoint(self, deployment_id: Any) -> Optional[DeploymentEventCheckpoint]:
        stmt = select(DeploymentEventCheckpoint).where(DeploymentEventCheckpoint.deployment_id == deployment_id).order_by(DeploymentEventCheckpoint.last_sequence_number.desc())
        result = await self.session.execute(stmt)
        return result.scalars().first()

    # Events
    async def create_event(self, event: DeploymentEvent) -> DeploymentEvent:
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def get_events(self, deployment_id: Any) -> List[DeploymentEvent]:
        stmt = select(DeploymentEvent).where(DeploymentEvent.deployment_id == deployment_id).order_by(DeploymentEvent.sequence_number.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_event(self, deployment_id: Any) -> Optional[DeploymentEvent]:
        stmt = select(DeploymentEvent).where(DeploymentEvent.deployment_id == deployment_id).order_by(DeploymentEvent.sequence_number.desc())
        result = await self.session.execute(stmt)
        return result.scalars().first()

    # Replay Metrics
    async def create_replay_metric(self, metric: DeploymentReplayMetric) -> DeploymentReplayMetric:
        self.session.add(metric)
        await self.session.flush()
        await self.session.refresh(metric)
        return metric

    async def list_replay_metrics(self, deployment_id: Any) -> List[DeploymentReplayMetric]:
        stmt = select(DeploymentReplayMetric).where(DeploymentReplayMetric.deployment_id == deployment_id).order_by(DeploymentReplayMetric.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Tags
    async def create_tag(self, tag: DeploymentTag) -> DeploymentTag:
        self.session.add(tag)
        await self.session.flush()
        await self.session.refresh(tag)
        return tag

    async def get_tags(self, deployment_id: Any) -> List[DeploymentTag]:
        stmt = select(DeploymentTag).where(DeploymentTag.deployment_id == deployment_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Approvals
    async def create_approval(self, approval: DeploymentApproval) -> DeploymentApproval:
        self.session.add(approval)
        await self.session.flush()
        await self.session.refresh(approval)
        return approval

    async def get_approval(self, id: Any) -> Optional[DeploymentApproval]:
        stmt = select(DeploymentApproval).where(DeploymentApproval.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_approval(self, approval: DeploymentApproval) -> DeploymentApproval:
        await self.session.flush()
        return approval

    async def get_approvals(self, deployment_id: Any) -> List[DeploymentApproval]:
        stmt = select(DeploymentApproval).where(DeploymentApproval.deployment_id == deployment_id).order_by(DeploymentApproval.reviewer_order.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Versions
    async def create_version(self, version: DeploymentVersion) -> DeploymentVersion:
        self.session.add(version)
        await self.session.flush()
        await self.session.refresh(version)
        return version

    async def get_versions(self, deployment_id: Any) -> List[DeploymentVersion]:
        stmt = select(DeploymentVersion).where(DeploymentVersion.deployment_id == deployment_id).order_by(DeploymentVersion.version_number.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Variables
    async def create_variable(self, variable: DeploymentEnvironmentVariable) -> DeploymentEnvironmentVariable:
        self.session.add(variable)
        await self.session.flush()
        await self.session.refresh(variable)
        return variable

    async def get_variables(self, deployment_id: Any) -> List[DeploymentEnvironmentVariable]:
        stmt = select(DeploymentEnvironmentVariable).where(DeploymentEnvironmentVariable.deployment_id == deployment_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Locks
    async def acquire_lock(self, lock: DeploymentJobLock) -> bool:
        stmt = select(DeploymentJobLock).where(DeploymentJobLock.environment_id == lock.environment_id).with_for_update()
        res = await self.session.execute(stmt)
        existing = res.scalars().first()
        now_dt = datetime.utcnow()
        if existing:
            if existing.expires_at < now_dt or existing.lease_owner == lock.lease_owner:
                existing.lease_owner = lock.lease_owner
                existing.acquired_at = lock.acquired_at
                existing.heartbeat_at = lock.heartbeat_at
                existing.expires_at = lock.expires_at
                await self.session.flush()
                return True
            return False
        else:
            self.session.add(lock)
            await self.session.flush()
            return True

    async def release_lock(self, environment_id: Any, lease_owner: Any) -> bool:
        stmt = select(DeploymentJobLock).where(
            and_(
                DeploymentJobLock.environment_id == environment_id,
                DeploymentJobLock.lease_owner == lease_owner
            )
        )
        res = await self.session.execute(stmt)
        existing = res.scalars().first()
        if existing:
            await self.session.delete(existing)
            await self.session.flush()
            return True
        return False

    async def heartbeat_lock(self, environment_id: Any, lease_owner: Any, duration_seconds: int) -> bool:
        stmt = select(DeploymentJobLock).where(
            and_(
                DeploymentJobLock.environment_id == environment_id,
                DeploymentJobLock.lease_owner == lease_owner
            )
        )
        res = await self.session.execute(stmt)
        existing = res.scalars().first()
        if existing:
            now_dt = datetime.utcnow()
            existing.heartbeat_at = now_dt
            existing.expires_at = datetime.fromtimestamp(now_dt.timestamp() + duration_seconds)
            await self.session.flush()
            return True
        return False

    async def get_lock(self, environment_id: Any) -> Optional[DeploymentJobLock]:
        stmt = select(DeploymentJobLock).where(DeploymentJobLock.environment_id == environment_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_expired_locks(self) -> List[DeploymentJobLock]:
        stmt = select(DeploymentJobLock).where(DeploymentJobLock.expires_at < datetime.utcnow())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    # Health & Telemetry Logs
    async def create_health_log(self, log: DeploymentHealthLog) -> DeploymentHealthLog:
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)
        return log

    async def get_health_logs(self, deployment_id: Any, limit: int = 100) -> List[DeploymentHealthLog]:
        stmt = select(DeploymentHealthLog).where(DeploymentHealthLog.deployment_id == deployment_id).order_by(DeploymentHealthLog.recorded_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_health_aggregates(self, deployment_id: Any) -> Dict[str, Any]:
        stmt = select(
            func.avg(DeploymentHealthLog.cpu_usage_pct).label("avg_cpu"),
            func.avg(DeploymentHealthLog.memory_usage_mb).label("avg_memory"),
            func.avg(DeploymentHealthLog.latency_ms).label("avg_latency"),
            func.avg(DeploymentHealthLog.throughput_rps).label("avg_throughput"),
            func.sum(DeploymentHealthLog.error_count).label("total_errors"),
            func.sum(case((DeploymentHealthLog.status == "UNHEALTHY", 1), else_=0)).label("unhealthy_count")
        ).where(DeploymentHealthLog.deployment_id == deployment_id)
        result = await self.session.execute(stmt)
        row = result.first()
        if row and row.avg_cpu is not None:
            return {
                "avg_cpu": float(row.avg_cpu),
                "avg_memory": float(row.avg_memory),
                "avg_latency": float(row.avg_latency),
                "avg_throughput": float(row.avg_throughput),
                "total_errors": int(row.total_errors),
                "unhealthy_count": int(row.unhealthy_count)
            }
        return {
            "avg_cpu": 0.0,
            "avg_memory": 0.0,
            "avg_latency": 0.0,
            "avg_throughput": 0.0,
            "total_errors": 0,
            "unhealthy_count": 0
        }

    # Freeze Windows
    async def create_freeze_window(self, window: DeploymentFreezeWindow) -> DeploymentFreezeWindow:
        self.session.add(window)
        await self.session.flush()
        await self.session.refresh(window)
        return window

    async def list_freeze_windows(self, project_id: Any) -> List[DeploymentFreezeWindow]:
        stmt = select(DeploymentFreezeWindow).where(DeploymentFreezeWindow.project_id == project_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
