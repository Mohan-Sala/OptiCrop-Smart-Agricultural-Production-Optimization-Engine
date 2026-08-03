import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.base import Base, AuditMixin


class TrainedModel(Base, AuditMixin):
    __tablename__ = "trained_models"

    training_session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("training_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True) # Default False, activated explicitly

    status: Mapped[str] = mapped_column(String(50), default="READY", nullable=False, index=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    hyperparameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    signature: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Active model timestamps
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    activated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    training_session: Mapped["TrainingSession"] = relationship(
        "TrainingSession", back_populates="trained_models"
    )
    metrics: Mapped[List["ModelMetric"]] = relationship(
        "ModelMetric", back_populates="trained_model", cascade="all, delete-orphan"
    )
    predictions: Mapped[List["PredictionHistory"]] = relationship(
        "PredictionHistory", back_populates="trained_model", cascade="all, delete-orphan"
    )
    evaluation_report: Mapped[Optional["EvaluationReport"]] = relationship(
        "EvaluationReport", back_populates="trained_model", cascade="all, delete-orphan", uselist=False
    )
    hyperparameter_set: Mapped[Optional["HyperparameterSet"]] = relationship(
        "HyperparameterSet", back_populates="trained_model", cascade="all, delete-orphan", uselist=False
    )
