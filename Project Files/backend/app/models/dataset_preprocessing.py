import uuid
from datetime import datetime
from typing import Any, Optional, Dict, List
from sqlalchemy import String, Integer, DateTime, ForeignKey, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class DatasetPreprocessing(Base, AuditMixin):
    __tablename__ = "dataset_preprocessing"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    preprocessed_dataset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING", index=True)
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    report: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Pipeline Hash & Lineage Versioning
    pipeline_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    preprocessing_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Environment Audits
    python_version: Mapped[str] = mapped_column(String(50), nullable=False)
    pandas_version: Mapped[str] = mapped_column(String(50), nullable=False)
    numpy_version: Mapped[str] = mapped_column(String(50), nullable=False)
    sklearn_version: Mapped[str] = mapped_column(String(50), nullable=False)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", foreign_keys=[dataset_id], back_populates="preprocessing_runs"
    )
    preprocessed_dataset: Mapped[Optional["Dataset"]] = relationship(
        "Dataset", foreign_keys=[preprocessed_dataset_id]
    )
    user: Mapped["User"] = relationship("User")
    project: Mapped["Project"] = relationship("Project")

    artifacts: Mapped[List["PreprocessingArtifact"]] = relationship(
        "PreprocessingArtifact", back_populates="preprocessing_run", cascade="all, delete-orphan"
    )
