import uuid
from datetime import datetime, timezone
from pydantic import Field
from beanie import Document


class AppDocument(Document):
    """Base document for all OptiCrop MongoDB Beanie models.
    
    Preserves UUID identifiers and standard UTC timestamps.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
    }

    class Settings:
        use_state_management = True
