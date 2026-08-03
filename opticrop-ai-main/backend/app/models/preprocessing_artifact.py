import uuid
from sqlalchemy import String, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class PreprocessingArtifact(Base, AuditMixin):
    __tablename__ = "preprocessing_artifacts"

    preprocessing_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("dataset_preprocessing.id", ondelete="CASCADE"), nullable=False, index=True
    )
    artifact_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Relationships
    preprocessing_run: Mapped["DatasetPreprocessing"] = relationship(
        "DatasetPreprocessing", back_populates="artifacts"
    )
