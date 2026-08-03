import uuid
from sqlalchemy import String, Float, ForeignKey, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class PredictionHistory(Base, AuditMixin):
    __tablename__ = "prediction_histories"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trained_model_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trained_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trained_model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    input_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    prediction: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="predictions")
    trained_model: Mapped["TrainedModel"] = relationship("TrainedModel", back_populates="predictions")
