import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class VersionedResponse(BaseModel):
    api_version: str = "v1"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthResponse(VersionedResponse):
    cache: str
    database: str
    aggregation: str


class DashboardResponse(VersionedResponse):
    project_id: uuid.UUID
    datasets_count: int
    preprocessing_runs_count: int
    training_sessions_count: int
    registered_models_count: int
    storage_usage_bytes: int
    active_model: Optional[Dict[str, Any]] = None
    recent_activity: List[Dict[str, Any]] = []


class ChartDTO(VersionedResponse):
    chart_type: str  # line, bar, scatter, heatmap, pie, timeline
    title: str
    series: List[Dict[str, Any]]
    axes: Dict[str, Any] = Field(default_factory=dict)
    legend: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ComparisonDTO(VersionedResponse):
    project_id: uuid.UUID
    comparison_table: List[Dict[str, Any]]
    metrics_deltas: Dict[str, Dict[str, float]]
    hyperparameters_comparison: Dict[str, Dict[str, Any]]


class LineageDTO(VersionedResponse):
    project_id: uuid.UUID
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class ExportResponse(VersionedResponse):
    project_id: uuid.UUID
    export_format: str
    content: str  # JSON string or CSV raw content
    filename: str
