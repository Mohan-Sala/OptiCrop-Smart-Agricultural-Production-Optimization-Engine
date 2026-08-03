import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.core.enums import AlertStatus, DriftStatus


class VersionedResponse(BaseModel):
    api_version: str = "v1"
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class AlertRuleCreate(BaseModel):
    metric_name: str
    threshold_value: float
    comparison_operator: str = ">"
    is_active: bool = True


class AlertRuleUpdate(BaseModel):
    threshold_value: Optional[float] = None
    comparison_operator: Optional[str] = None
    is_active: Optional[bool] = None


class AlertRuleResponse(VersionedResponse):
    id: uuid.UUID
    project_id: uuid.UUID
    metric_name: str
    threshold_value: float
    comparison_operator: str
    is_active: bool
    created_at: datetime


class AlertDTO(BaseModel):
    id: uuid.UUID
    rule_name: str
    severity: str
    message: str
    occurrence_count: int
    last_triggered_at: datetime
    status: AlertStatus
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[uuid.UUID] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[uuid.UUID] = None


class SubsystemHealthDTO(BaseModel):
    healthy: bool
    last_check: datetime
    latency_ms: float
    details: Dict[str, Any] = {}


class DiagnosticHealthDTO(BaseModel):
    database: SubsystemHealthDTO
    cache: SubsystemHealthDTO
    scheduler: SubsystemHealthDTO
    background_workers: SubsystemHealthDTO
    telemetry_providers: SubsystemHealthDTO
    storage: SubsystemHealthDTO
    event_bus: SubsystemHealthDTO
    overall_status: str


class FeatureDriftMetadataDTO(BaseModel):
    feature_name: str
    baseline_mean: float
    baseline_std: float
    current_mean: float
    current_std: float
    drift_score: float
    drift_detected: bool
    importance_rank: Optional[int] = None


class MonitoringSnapshot(VersionedResponse):
    project_id: uuid.UUID
    model_id: uuid.UUID
    prediction_count: int
    success_rate: float
    cache_hit_ratio: float
    avg_latency_ms: float
    health: DiagnosticHealthDTO
    active_alerts: List[AlertDTO]
    feature_drifts: List[FeatureDriftMetadataDTO]
    overall_drift_score: float
    is_drifted: bool


class HealthResponse(VersionedResponse):
    status: str
    health_details: DiagnosticHealthDTO


class DriftResponse(VersionedResponse):
    model_id: uuid.UUID
    overall_drift_score: float
    is_drifted: bool
    status: DriftStatus
    feature_drifts: List[FeatureDriftMetadataDTO]
    target_drift: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class MetricSeriesDTO(BaseModel):
    timestamp: datetime
    value: float


class TimeSeriesDTO(BaseModel):
    predictions: List[MetricSeriesDTO]
    latency: List[MetricSeriesDTO]
    errors: List[MetricSeriesDTO]


class ModelMonitoringResponse(VersionedResponse):
    model_id: uuid.UUID
    prediction_count: int
    cache_hit_ratio: float
    avg_inference_latency: float
    timeseries: TimeSeriesDTO


class MonitoringOverviewResponse(VersionedResponse):
    total_predictions: int
    success_rate: float
    avg_latency_ms: float
    active_alerts_count: int
    active_models_count: int


class ExternalTelemetryIngestRequest(BaseModel):
    provider_name: str
    source_id: Optional[str] = None
    provider_record_id: Optional[str] = None
    recorded_at: datetime
    payload: Dict[str, Any]


class MonitoringExportResponse(VersionedResponse):
    project_id: uuid.UUID
    export_format: str
    content: str
    filename: str
