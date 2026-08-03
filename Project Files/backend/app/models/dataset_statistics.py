import uuid
from typing import Any
from sqlalchemy import BigInteger, ForeignKey, Integer, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class DatasetStatistics(Base, AuditMixin):
    __tablename__ = "dataset_statistics"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("datasets.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    missing_values: Mapped[Any] = mapped_column(JSON, nullable=True)
    duplicate_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_columns: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    memory_usage: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    column_summary: Mapped[Any] = mapped_column(JSON, nullable=True)

    # Relationships
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="statistics")
