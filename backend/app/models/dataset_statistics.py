import uuid
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class DatasetStatisticsEmbedded(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    dataset_id: uuid.UUID
    missing_values: Optional[Dict[str, Any]] = None
    duplicate_rows: int = 0
    duplicate_columns: int = 0
    memory_usage: int = 0
    column_summary: Optional[Dict[str, Any]] = None


class DatasetStatistics(AppDocument):
    dataset_id: uuid.UUID
    missing_values: Optional[Dict[str, Any]] = None
    duplicate_rows: int = 0
    duplicate_columns: int = 0
    memory_usage: int = 0
    column_summary: Optional[Dict[str, Any]] = None

    class Settings:
        name = "dataset_statistics"
        indexes = [
            IndexModel([("dataset_id", ASCENDING)], unique=True),
        ]
