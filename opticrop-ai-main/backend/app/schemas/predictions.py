import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class VersionedResponse(BaseModel):
    api_version: str = "v1"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SinglePredictionRequest(BaseModel):
    project_id: uuid.UUID
    model_id: Optional[uuid.UUID] = None
    features: Dict[str, Any]
    include_explanation: bool = False


class BatchPredictionRequest(BaseModel):
    project_id: uuid.UUID
    model_id: Optional[uuid.UUID] = None
    features_list: List[Dict[str, Any]]
    include_explanation: bool = False


class PredictionResponse(VersionedResponse):
    prediction_id: uuid.UUID
    model_id: uuid.UUID
    model_version: int
    prediction_timestamp: datetime
    execution_time_ms: float
    predictions: List[Any]
    confidence_scores: Optional[List[float]] = None
    prediction_metadata: Dict[str, Any] = {}


class PredictionRunResponse(VersionedResponse):
    id: uuid.UUID
    project_id: uuid.UUID
    model_id: uuid.UUID
    model_version: int
    status: str
    prediction_count: int
    execution_time: float
    prediction_timestamp: datetime
    predictions: Optional[List[Any]] = None
    confidence_scores: Optional[List[float]] = None
    error_message: Optional[str] = None


class PredictionHealthResponse(VersionedResponse):
    status: str = "healthy"
    loaded_model_cache_count: int
    prediction_cache_statistics: Dict[str, Any]
    storage_connectivity: str
    average_prediction_latency_ms: float
    queued_batch_jobs: int
    active_inference_workers: int


class PredictionExportResponse(VersionedResponse):
    project_id: uuid.UUID
    export_format: str
    content: str
    filename: str
