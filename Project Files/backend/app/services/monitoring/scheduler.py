import uuid
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy import select, update, delete
from app.models.monitoring_job_lock import MonitoringJobLock
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("app.services.monitoring.scheduler")


class MonitoringScheduler:
    """Resilient background scheduler managing database-backed job locks lease contracts."""

    def __init__(self, session: AsyncSession, lease_owner_id: Optional[uuid.UUID] = None):
        self.session = session
        self.lease_owner = lease_owner_id or uuid.uuid4()

    async def acquire_lock(self, job_name: str, lease_duration_seconds: int = 300) -> bool:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=lease_duration_seconds)
        
        stmt = select(MonitoringJobLock).where(MonitoringJobLock.job_name == job_name)
        result = await self.session.execute(stmt)
        lock = result.scalars().first()
        
        if not lock:
            lock = MonitoringJobLock(
                job_name=job_name,
                lease_owner=self.lease_owner,
                acquired_at=now,
                heartbeat_at=now,
                expires_at=expires
            )
            self.session.add(lock)
            try:
                await self.session.flush()
                await self.session.commit()
                return True
            except Exception:
                await self.session.rollback()
                return False
                
        if lock.expires_at < now or lock.lease_owner == self.lease_owner:
            lock.lease_owner = self.lease_owner
            lock.acquired_at = now
            lock.heartbeat_at = now
            lock.expires_at = expires
            try:
                await self.session.flush()
                await self.session.commit()
                return True
            except Exception:
                await self.session.rollback()
                return False
                
        return False

    async def heartbeat(self, job_name: str, extend_seconds: int = 300) -> None:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=extend_seconds)
        stmt = (
            update(MonitoringJobLock)
            .where(
                MonitoringJobLock.job_name == job_name,
                MonitoringJobLock.lease_owner == self.lease_owner
            )
            .values(heartbeat_at=now, expires_at=expires)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def release_lock(self, job_name: str) -> None:
        stmt = delete(MonitoringJobLock).where(
            MonitoringJobLock.job_name == job_name,
            MonitoringJobLock.lease_owner == self.lease_owner
        )
        await self.session.execute(stmt)
        await self.session.commit()
