import uuid
from sqlalchemy import String, Boolean, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, AuditMixin


class UserSetting(Base, AuditMixin):
    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    theme: Mapped[str] = mapped_column(String(50), default="system", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="settings")
