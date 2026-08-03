import uuid
from sqlalchemy import String, ForeignKey, Uuid, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class FeatureMetadata(Base, AuditMixin):
    __tablename__ = "feature_metadata"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    feature_name: Mapped[str] = mapped_column(String(255), nullable=False)
    feature_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # NUMERIC, CATEGORICAL, TARGET
    
    nullable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    encoded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scaled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    target: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    # Relationships
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="feature_catalog")
