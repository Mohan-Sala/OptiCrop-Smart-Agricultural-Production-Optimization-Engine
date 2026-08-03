import uuid
from typing import Dict, Any
from sqlalchemy import ForeignKey, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class HyperparameterSet(Base, AuditMixin):
    __tablename__ = "hyperparameter_sets"

    trained_model_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trained_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Relationships
    trained_model: Mapped["TrainedModel"] = relationship("TrainedModel", back_populates="hyperparameter_set")
