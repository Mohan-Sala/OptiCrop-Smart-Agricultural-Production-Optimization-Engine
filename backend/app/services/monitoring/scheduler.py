import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from app.models.monitoring_job_lock import MonitoringJobLock

logger = logging.getLogger("app.services.monitoring.scheduler")


class MonitoringScheduler:
    """Resilient background scheduler managing database-backed job locks lease contracts."""

    def __init__(self, session=None, lease_owner_id: Optional[uuid.UUID] = None):
        self.session = session
        self.lease_owner = lease_owner_id or uuid.uuid4()

    async def acquire_lock(self, job_name: str, lease_duration_seconds: int = 300) -> bool:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=lease_duration_seconds)
        
        lock = await MonitoringJobLock.find_one(MonitoringJobLock.job_name == job_name)
        
        if not lock:
            lock = MonitoringJobLock(
                job_name=job_name,
                lease_owner=self.lease_owner,
                acquired_at=now,
                heartbeat_at=now,
                expires_at=expires,
            )
            try:
                await lock.insert()
                return True
            except Exception:
                return False
                
        if lock.expires_at < now or lock.lease_owner == self.lease_owner:
            lock.lease_owner = self.lease_owner
            lock.acquired_at = now
            lock.heartbeat_at = now
            lock.expires_at = expires
            try:
                await lock.save()
                return True
            except Exception:
                return False
                
        return False

    async def heartbeat(self, job_name: str, extend_seconds: int = 300) -> None:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=extend_seconds)
        await MonitoringJobLock.find(
            MonitoringJobLock.job_name == job_name,
            MonitoringJobLock.lease_owner == self.lease_owner,
        ).update({"$set": {"heartbeat_at": now, "expires_at": expires}})

    async def release_lock(self, job_name: str) -> None:
        await MonitoringJobLock.find(
            MonitoringJobLock.job_name == job_name,
            MonitoringJobLock.lease_owner == self.lease_owner,
        ).delete()
