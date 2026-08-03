import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Float, Integer, DateTime, Enum, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin
from app.core.enums import AlertStatus


class MonitoringAlert(Base, AuditMixin):
    __tablename__ = "monitoring_alerts"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trained_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("alert_rules.id", ondelete="SET NULL"), nullable=True, index=True
    )
    rule_name: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=True)
    threshold_value: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alert_status"), default=AlertStatus.ACTIVE, nullable=False, index=True
    )

    occurrence_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Lifecycle tracing
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_by: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    model: Mapped["TrainedModel"] = relationship("TrainedModel")
    rule: Mapped["AlertRule"] = relationship("AlertRule", back_populates="alerts")
