import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class MonitoringJobLock(Base):
    __tablename__ = "monitoring_job_locks"

    job_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    lease_owner: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    heartbeat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
