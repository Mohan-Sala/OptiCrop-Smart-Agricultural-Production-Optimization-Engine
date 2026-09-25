import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.core.enums import DatasetStatus, DatasetStage


class DatasetStatisticsResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    missing_values: Optional[Dict[str, int]] = None
    duplicate_rows: int = 0
    duplicate_columns: int = 0
    memory_usage: int = 0
    column_summary: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    original_filename: str
    stored_filename: str
    storage_path: str
    version: int
    parent_dataset_id: Optional[uuid.UUID] = None
    is_latest: bool
    dataset_stage: DatasetStage
    status: DatasetStatus
    rows: int
    columns: int
    size: int
    delimiter: Optional[str] = None
    encoding: Optional[str] = None
    sha256_checksum: Optional[str] = None
    is_locked: bool
    locked_by_training: bool
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    uploaded_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetDetailsResponse(DatasetResponse):
    statistics: Optional[DatasetStatisticsResponse] = None


class DatasetListResponse(BaseModel):
    items: List[DatasetResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DatasetRenameRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None


class DatasetPreviewResponse(BaseModel):
    dataset_id: uuid.UUID
    shape: List[int] = Field(..., description="[rows, columns]")
    columns: List[str] = Field(..., description="Column names")
    dtypes: Dict[str, str] = Field(..., description="Column data types")
    missing_values: Dict[str, int] = Field(..., description="Null values count per column")
    memory_usage_bytes: int
    data: List[Dict[str, Any]] = Field(..., description="First 10 rows of the dataset")


class ValidationErrorDetail(BaseModel):
    loc: List[str]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: List[ValidationErrorDetail]
