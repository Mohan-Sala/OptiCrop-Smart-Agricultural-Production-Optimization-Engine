import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Union, List
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class PredictionStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PredictionRun(AppDocument):
    user_id: uuid.UUID
    project_id: uuid.UUID
    model_id: uuid.UUID
    model_version: int
    model_checksum: str
    model_signature_checksum: str
    dataset_version: int
    preprocessing_run_id: Optional[uuid.UUID] = None
    
    prediction_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time: float = 0.0
    prediction_count: int = 0
    request_hash: str
    idempotency_key: Optional[str] = None
    
    status: PredictionStatus = PredictionStatus.PENDING
    
    request_payload: Optional[Union[Dict[str, Any], List[Any]]] = None
    preprocessed_features: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    prediction_response: Optional[Dict[str, Any]] = None
    
    # Future explainability placeholders
    explanation_status: str = "NOT_REQUESTED"
    explanation_payload: Optional[Dict[str, Any]] = None
    feature_contributions: Optional[Dict[str, Any]] = None
    
    # Timing checkpoints (Phase 9 monitoring readiness)
    timing_validation: float = 0.0
    timing_preprocessing: float = 0.0
    timing_loading: float = 0.0
    timing_prediction: float = 0.0
    timing_serialization: float = 0.0
    error_message: Optional[str] = None

    class Settings:
        name = "prediction_runs"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("project_id", ASCENDING)]),
            IndexModel([("model_id", ASCENDING)]),
            IndexModel([("project_id", ASCENDING), ("created_at", ASCENDING)]),
            IndexModel([("model_id", ASCENDING), ("created_at", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("request_hash", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("idempotency_key", ASCENDING)]),
        ]
