import uuid
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class TrainingExperiment(Base, AuditMixin):
    __tablename__ = "training_experiments"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="experiments")
    training_sessions: Mapped[List["TrainingSession"]] = relationship(
        "TrainingSession", back_populates="experiment", cascade="all, delete-orphan"
    )
