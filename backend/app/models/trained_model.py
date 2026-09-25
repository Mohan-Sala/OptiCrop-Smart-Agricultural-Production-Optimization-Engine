import uuid
from datetime import datetime
from typing import Optional, Dict, Any, Union
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class TrainedModel(AppDocument):
    training_session_id: uuid.UUID
    model_name: str
    algorithm: str
    storage_path: str
    version: Union[str, int] = "1.0.0"
    is_active: bool = False

    status: str = "READY"
    checksum: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    signature: Optional[Dict[str, Any]] = None

    # Active model timestamps
    activated_at: Optional[datetime] = None
    activated_by: Optional[uuid.UUID] = None

    class Settings:
        name = "trained_models"
        indexes = [
            IndexModel([("training_session_id", ASCENDING)]),
            IndexModel([("is_active", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("algorithm", ASCENDING)]),
        ]
