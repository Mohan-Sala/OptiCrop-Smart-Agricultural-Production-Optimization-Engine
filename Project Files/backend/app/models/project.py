import uuid
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class Project(Base, AuditMixin):
    __tablename__ = "projects"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="projects")
    datasets: Mapped[List["Dataset"]] = relationship(
        "Dataset", back_populates="project", cascade="all, delete-orphan"
    )
    experiments: Mapped[List["TrainingExperiment"]] = relationship(
        "TrainingExperiment", back_populates="project", cascade="all, delete-orphan"
    )
    alert_rules: Mapped[List["AlertRule"]] = relationship(
        "AlertRule", back_populates="project", cascade="all, delete-orphan"
    )
