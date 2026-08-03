import enum
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, Integer, ForeignKey, JSON, Uuid, DateTime, Enum, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database.base import Base, AuditMixin


class PredictionStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PredictionRun(Base, AuditMixin):
    __tablename__ = "prediction_runs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trained_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_version: Mapped[int] = mapped_column(Integer, nullable=False)
    model_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    model_signature_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    dataset_version: Mapped[int] = mapped_column(Integer, nullable=False)
    preprocessing_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("dataset_preprocessing.id", ondelete="SET NULL"), nullable=True
    )
    
    prediction_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    execution_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    prediction_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    status: Mapped[PredictionStatus] = mapped_column(
        Enum(PredictionStatus, name="prediction_status_enum", inherit_schema=True),
        default=PredictionStatus.PENDING,
        nullable=False,
        index=True
    )
    
    request_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    preprocessed_features: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    prediction_response: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Future explainability placeholders
    explanation_status: Mapped[str] = mapped_column(String(50), default="NOT_REQUESTED", nullable=False)
    explanation_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    feature_contributions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing checkpoints (Phase 9 monitoring readiness)
    timing_validation: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    timing_preprocessing: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    timing_loading: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    timing_prediction: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    timing_serialization: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    __table_args__ = (
        Index("idx_prediction_runs_project_created_at", "project_id", "created_at"),
        Index("idx_prediction_runs_model_created_at", "model_id", "created_at"),
        Index("idx_prediction_runs_status", "status"),
        UniqueConstraint("user_id", "idempotency_key", name="uq_user_idempotency"),
    )
