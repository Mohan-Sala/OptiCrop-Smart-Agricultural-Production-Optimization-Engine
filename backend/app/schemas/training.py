import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExperimentCreateRequest(BaseModel):
    project_id: uuid.UUID
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class ExperimentResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrainingConfigRequest(BaseModel):
    experiment_id: uuid.UUID
    dataset_id: uuid.UUID
    problem_type: str = Field("classification", description="classification or regression")
    algorithms: List[str] = Field(..., description="RandomForest, SVM, LogisticRegression, KNN, GradientBoosting, etc.")
    hyperparameters: Optional[Dict[str, Dict[str, List[Any]]]] = Field(default_factory=dict)
    cv_strategy: Optional[Dict[str, Any]] = Field(default_factory=lambda: {"method": "KFold", "folds": 5})
    training_seed: Optional[int] = 42
    test_size: Optional[float] = 0.2
    shuffle: Optional[bool] = True


class TrainingSessionResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    experiment_id: Optional[uuid.UUID] = None
    preprocessing_run_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    problem_type: str
    target_column: str
    status: str
    best_model: Optional[str] = None
    training_time: Optional[float] = None
    storage_model_path: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    training_seed: Optional[int] = None
    test_size: Optional[float] = None
    config_hash: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModelMetricResponse(BaseModel):
    metric_name: str
    metric_value: float

    model_config = ConfigDict(from_attributes=True)


class TrainedModelResponse(BaseModel):
    id: uuid.UUID
    training_session_id: uuid.UUID
    model_name: str
    algorithm: str
    storage_path: str
    version: str
    is_active: bool
    status: str
    checksum: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    signature: Optional[Dict[str, Any]] = None
    activated_at: Optional[datetime] = None
    activated_by: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrainedModelDetailsResponse(TrainedModelResponse):
    metrics: List[ModelMetricResponse] = []
    evaluation_report: Optional[Dict[str, Any]] = None

    @classmethod
    def model_validate(cls, obj: Any, *args, **kwargs):
        # Flatten report_data from EvaluationReport relation if present
        validated = super().model_validate(obj, *args, **kwargs)
        if getattr(obj, "evaluation_report", None):
            validated.evaluation_report = obj.evaluation_report.report_data
        return validated
