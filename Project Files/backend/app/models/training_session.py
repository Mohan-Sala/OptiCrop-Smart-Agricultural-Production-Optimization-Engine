import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Float, DateTime, ForeignKey, Uuid, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class TrainingSession(Base, AuditMixin):
    __tablename__ = "training_sessions"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    experiment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("training_experiments.id", ondelete="CASCADE"), nullable=True, index=True
    )
    preprocessing_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("dataset_preprocessing.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    problem_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_column: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)
    
    # Reproducible seeds and splits configs
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    training_seed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    test_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    shuffle: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    stratify_column: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cv_seed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    config_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    best_model: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    training_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    storage_model_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="training_sessions")
    experiment: Mapped[Optional["TrainingExperiment"]] = relationship("TrainingExperiment", back_populates="training_sessions")
    preprocessing_run: Mapped[Optional["DatasetPreprocessing"]] = relationship("DatasetPreprocessing")
    user: Mapped[Optional["User"]] = relationship("User")
    trained_models: Mapped[List["TrainedModel"]] = relationship(
        "TrainedModel", back_populates="training_session", cascade="all, delete-orphan"
    )
