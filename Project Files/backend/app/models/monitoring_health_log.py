from datetime import datetime
from sqlalchemy import Boolean, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base, AuditMixin


class MonitoringHealthLog(Base, AuditMixin):
    __tablename__ = "monitoring_health_logs"

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    database_healthy: Mapped[bool] = mapped_column(Boolean, nullable=False)
    storage_healthy: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cache_healthy: Mapped[bool] = mapped_column(Boolean, nullable=False)
    worker_healthy: Mapped[bool] = mapped_column(Boolean, nullable=False)
    response_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)
