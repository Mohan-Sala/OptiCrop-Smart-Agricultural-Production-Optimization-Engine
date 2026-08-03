import uuid
from sqlalchemy import String, Float, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class ModelMetric(Base, AuditMixin):
    __tablename__ = "model_metrics"

    trained_model_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trained_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    trained_model: Mapped["TrainedModel"] = relationship("TrainedModel", back_populates="metrics")
