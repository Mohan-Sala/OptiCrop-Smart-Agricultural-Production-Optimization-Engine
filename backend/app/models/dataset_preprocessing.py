import uuid
from datetime import datetime
from typing import Any, Optional, Dict
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class DatasetPreprocessing(AppDocument):
    dataset_id: uuid.UUID
    preprocessed_dataset_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    project_id: uuid.UUID

    status: str = "PENDING"
    parameters: Dict[str, Any]
    report: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    # Pipeline Hash & Lineage Versioning
    pipeline_version: int = 1
    preprocessing_hash: str

    # Environment Audits
    python_version: str
    pandas_version: str
    numpy_version: str
    sklearn_version: str

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Settings:
        name = "dataset_preprocessing"
        indexes = [
            IndexModel([("dataset_id", ASCENDING)]),
            IndexModel([("preprocessed_dataset_id", ASCENDING)]),
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("project_id", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("preprocessing_hash", ASCENDING)]),
        ]
