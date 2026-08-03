import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Float, Boolean, DateTime, JSON, Enum, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin
from app.core.enums import DriftStatus


class DriftSnapshot(Base, AuditMixin):
    __tablename__ = "drift_snapshots"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trained_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    method_name: Mapped[str] = mapped_column(String(50), nullable=False)
    drift_score: Mapped[float] = mapped_column(Float, nullable=False)
    is_drifted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    feature_drifts: Mapped[dict] = mapped_column(JSON, nullable=False)
    target_drift: Mapped[dict] = mapped_column(JSON, nullable=True)

    baseline_statistics_version: Mapped[str] = mapped_column(String(64), nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[DriftStatus] = mapped_column(
        Enum(DriftStatus, name="drift_status"), default=DriftStatus.PENDING, nullable=False, index=True
    )
    error_message: Mapped[str] = mapped_column(String(1000), nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    model: Mapped["TrainedModel"] = relationship("TrainedModel")
