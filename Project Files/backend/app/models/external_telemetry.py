import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class ExternalTelemetryLog(Base, AuditMixin):
    __tablename__ = "external_telemetry_logs"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_id: Mapped[str] = mapped_column(String(100), nullable=True)
    provider_record_id: Mapped[str] = mapped_column(String(100), nullable=True)
    ingestion_status: Mapped[str] = mapped_column(String(20), nullable=False, default="VALIDATED")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    normalized_payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project")
