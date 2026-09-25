import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument
from app.core.enums import DatasetStatus, DatasetStage
from app.models.dataset_statistics import DatasetStatisticsEmbedded


class Dataset(AppDocument):
    project_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    original_filename: str
    stored_filename: str
    storage_path: str
    
    # Versioning & Lineage
    version: int = 1
    parent_dataset_id: Optional[uuid.UUID] = None
    is_latest: bool = True
    dataset_stage: DatasetStage = DatasetStage.RAW

    # Status & Analytical Metadata
    status: DatasetStatus = DatasetStatus.UPLOADING
    rows: int = 0
    columns: int = 0
    size: int = 0
    delimiter: Optional[str] = None
    encoding: Optional[str] = None
    sha256_checksum: Optional[str] = None

    # Locking & Soft Delete
    is_locked: bool = False
    locked_by_training: bool = False
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    # User Metadata
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Statistics and feature catalog relations
    statistics: Optional[Any] = None
    feature_catalog: Optional[List[Any]] = None

    class Settings:
        name = "datasets"
        indexes = [
            IndexModel([("project_id", ASCENDING)]),
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("is_latest", ASCENDING)]),
            IndexModel([("is_deleted", ASCENDING)]),
            IndexModel([("project_id", ASCENDING), ("name", ASCENDING), ("version", ASCENDING)]),
        ]
