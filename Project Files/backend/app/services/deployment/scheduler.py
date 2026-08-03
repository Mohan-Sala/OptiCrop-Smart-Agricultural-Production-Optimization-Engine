import logging
from datetime import datetime, timezone, timedelta
from typing import List
import uuid

from sqlalchemy import delete
from app.models.deployment import DeploymentJobLock, DeploymentApproval, DeploymentEventCheckpoint, DeploymentSetting
from app.repositories.interfaces.deployment import DeploymentRepository

logger = logging.getLogger(__name__)

class DeploymentSchedulerService:
    """Service executing recurring background jobs: lock cleanup, checkpoint retention, and approval evictions."""

    def __init__(self, repo: DeploymentRepository):
        self.repo = repo

    async def prune_expired_locks(self) -> int:
        """Finds and releases all active locks whose lease duration has expired."""
        expired = await self.repo.list_expired_locks()
        count = 0
        for lock in expired:
            released = await self.repo.release_lock(lock.environment_id, lock.lease_owner)
            if released:
                count += 1
        if count > 0:
            logger.info(f"Background Job: Pruned {count} expired deployment locks.")
        return count

    async def enforce_checkpoint_retention(self, project_id: uuid.UUID) -> int:
        """Prunes historical checkpoints exceeding the configured retention threshold for a project."""
        settings = await self.repo.get_settings(project_id)
        retention_days = settings.checkpoint_retention_days if settings else 30

        # Retrieve checkpoints for all deployments in the project
        environments = await self.repo.list_environments(project_id)
        count = 0
        now_dt = datetime.now(timezone.utc)
        
        for env in environments:
            for deployment in env.deployments:
                # Iterate and delete checkpoints older than retention_days
                # Note: We can implement delete logic inside repo or execute direct delete statement
                # For simplicity, filter in Python and delete
                # Let's delete checkpoint records older than (now - retention_days)
                # Since SQLAlchemy cascade handles snapshots, this is clean
                pass
        
        # We can implement a clean bulk delete based on date
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        # Execute delete query via repo session
        from sqlalchemy import delete
        stmt = delete(DeploymentEventCheckpoint).where(
            DeploymentEventCheckpoint.created_at < cutoff_date
        )
        result = await self.repo.session.execute(stmt)
        deleted_count = result.rowcount
        if deleted_count > 0:
            logger.info(f"Background Job: Pruned {deleted_count} checkpoints older than {retention_days} days.")
        return deleted_count

    async def evict_expired_approvals(self, approval_expiry_hours: int = 48) -> int:
        """Evicts pending approvals or cancels deployments where approvals have expired."""
        # Evict pending approval records older than approval_expiry_hours
        cutoff = datetime.utcnow() - timedelta(hours=approval_expiry_hours)
        stmt = delete(DeploymentApproval).where(
            (DeploymentApproval.decision == "PENDING") & (DeploymentApproval.decided_at < cutoff)
        )
        result = await self.repo.session.execute(stmt)
        deleted_count = result.rowcount
        if deleted_count > 0:
            logger.info(f"Background Job: Evicted {deleted_count} expired pending approvals.")
        return deleted_count
