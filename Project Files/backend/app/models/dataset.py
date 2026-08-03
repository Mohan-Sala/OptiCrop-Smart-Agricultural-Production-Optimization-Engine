import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, BigInteger, DateTime, ForeignKey, Uuid, Boolean, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.base import Base, AuditMixin
from app.core.enums import DatasetStatus, DatasetStage


class Dataset(Base, AuditMixin):
    __tablename__ = "datasets"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Versioning & Lineage
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_dataset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True
    )
    is_latest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    dataset_stage: Mapped[DatasetStage] = mapped_column(
        Enum(DatasetStage, name="dataset_stage"), nullable=False, default=DatasetStage.RAW, index=True
    )

    # Status & Analytical Metadata
    status: Mapped[DatasetStatus] = mapped_column(
        Enum(DatasetStatus, name="dataset_status"), default=DatasetStatus.UPLOADING, nullable=False, index=True
    )
    rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    columns: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    delimiter: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    encoding: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sha256_checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)

    # Locking & Soft Delete
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    locked_by_training: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # User Metadata
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="datasets")
    user: Mapped["User"] = relationship("User", back_populates="datasets")
    training_sessions: Mapped[List["TrainingSession"]] = relationship(
        "TrainingSession", back_populates="dataset", cascade="all, delete-orphan"
    )
    statistics: Mapped[Optional["DatasetStatistics"]] = relationship(
        "DatasetStatistics", back_populates="dataset", cascade="all, delete-orphan", uselist=False
    )
    parent_dataset: Mapped[Optional["Dataset"]] = relationship(
        "Dataset", remote_side="Dataset.id", backref="derived_datasets"
    )
    preprocessing_runs: Mapped[List["DatasetPreprocessing"]] = relationship(
        "DatasetPreprocessing", foreign_keys="[DatasetPreprocessing.dataset_id]", back_populates="dataset", cascade="all, delete-orphan"
    )
    feature_catalog: Mapped[List["FeatureMetadata"]] = relationship(
        "FeatureMetadata", back_populates="dataset", cascade="all, delete-orphan"
    )
