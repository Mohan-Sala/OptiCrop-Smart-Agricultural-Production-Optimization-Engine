import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class TrainingSession(AppDocument):
    dataset_id: uuid.UUID
    experiment_id: Optional[uuid.UUID] = None
    preprocessing_run_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None

    problem_type: str
    target_column: str
    status: str = "pending"
    
    # Reproducible seeds and splits configs
    config: Optional[Dict[str, Any]] = None
    training_seed: Optional[int] = None
    test_size: Optional[float] = None
    shuffle: Optional[bool] = None
    stratify_column: Optional[str] = None
    cv_seed: Optional[int] = None
    config_hash: Optional[str] = None

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    best_model: Optional[str] = None
    training_time: Optional[float] = None
    storage_model_path: Optional[str] = None

    class Settings:
        name = "training_sessions"
        indexes = [
            IndexModel([("dataset_id", ASCENDING)]),
            IndexModel([("experiment_id", ASCENDING)]),
            IndexModel([("preprocessing_run_id", ASCENDING)]),
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("config_hash", ASCENDING)]),
        ]
