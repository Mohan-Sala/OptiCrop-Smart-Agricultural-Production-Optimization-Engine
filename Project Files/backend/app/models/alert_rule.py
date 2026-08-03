import uuid
from sqlalchemy import String, ForeignKey, Float, Boolean, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class AlertRule(Base, AuditMixin):
    __tablename__ = "alert_rules"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_name: Mapped[str] = mapped_column(String(50), nullable=False)
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    comparison_operator: Mapped[str] = mapped_column(String(10), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="alert_rules")
    alerts: Mapped[list["MonitoringAlert"]] = relationship(
        "MonitoringAlert", back_populates="rule", cascade="all, delete-orphan"
    )
