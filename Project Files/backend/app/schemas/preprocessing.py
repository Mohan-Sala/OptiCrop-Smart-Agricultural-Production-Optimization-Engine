import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MissingValueStrategies(BaseModel):
    numeric_strategy: str = Field("median", description="mean, median, mode, constant, drop_rows, drop_columns")
    categorical_strategy: str = Field("most_frequent", description="most_frequent, constant, drop_rows, drop_columns")
    columns_overrides: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OutlierStrategy(BaseModel):
    method: str = Field("IQR", description="IQR, Z-Score")
    action: str = Field("flag_only", description="flag_only, remove")


class PreprocessingConfigRequest(BaseModel):
    target_column: str
    missing_value_strategies: MissingValueStrategies = Field(default_factory=MissingValueStrategies)
    outlier_strategy: OutlierStrategy = Field(default_factory=OutlierStrategy)
    encoding_mappings: Dict[str, str] = Field(default_factory=dict, description="OneHotEncoder, LabelEncoder, OrdinalEncoder")
    scaling_mappings: Dict[str, str] = Field(default_factory=dict, description="StandardScaler, MinMaxScaler, RobustScaler, Normalizer")


class PreprocessingArtifactResponse(BaseModel):
    id: uuid.UUID
    artifact_type: str
    storage_path: str
    checksum: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreprocessingRunResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    preprocessed_dataset_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    project_id: uuid.UUID
    status: str
    parameters: Dict[str, Any]
    report: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    pipeline_version: int
    preprocessing_hash: str
    python_version: str
    pandas_version: str
    numpy_version: str
    sklearn_version: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreprocessingRunDetailsResponse(PreprocessingRunResponse):
    artifacts: List[PreprocessingArtifactResponse] = []


class PreprocessingHistoryResponse(BaseModel):
    items: List[PreprocessingRunResponse]
    total: int


class FeatureMetadataResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    feature_name: str
    feature_type: str
    nullable: bool
    encoded: bool
    scaled: bool
    generated: bool
    target: bool

    model_config = ConfigDict(from_attributes=True)
