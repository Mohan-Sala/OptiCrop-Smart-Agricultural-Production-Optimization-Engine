import uuid
from datetime import datetime
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class MonitoringJobLock(AppDocument):
    job_name: str
    lease_owner: uuid.UUID
    acquired_at: datetime
    heartbeat_at: datetime
    expires_at: datetime

    class Settings:
        name = "monitoring_job_locks"
        indexes = [
            IndexModel([("job_name", ASCENDING)], unique=True),
        ]
