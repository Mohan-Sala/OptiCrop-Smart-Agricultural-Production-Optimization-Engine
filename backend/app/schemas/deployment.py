import uuid
from datetime import datetime, time, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class VersionedResponse(BaseModel):
    api_version: str = "v1"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Environments
class DeploymentEnvironmentCreate(BaseModel):
    name: str = Field(..., max_length=50)
    is_production: bool = False
    description: Optional[str] = Field(None, max_length=255)


class DeploymentEnvironmentResponse(VersionedResponse):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    is_production: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


# Settings
class DeploymentSettingsUpdate(BaseModel):
    checkpoint_interval: int = Field(100, ge=1)
    checkpoint_retention_days: int = Field(30, ge=1)


class DeploymentSettingsResponse(VersionedResponse):
    project_id: uuid.UUID
    checkpoint_interval: int
    checkpoint_retention_days: int
    created_at: datetime
    updated_at: datetime


# Policies
class DeploymentPolicyCreate(BaseModel):
    name: str = Field(..., max_length=100)
    required_approvals: int = Field(1, ge=0)
    required_reviewer_roles: Optional[str] = Field(None, max_length=100)
    maximum_latency_ms: Optional[float] = Field(None, ge=0.0)
    maximum_error_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    minimum_success_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    minimum_throughput: Optional[float] = Field(None, ge=0.0)
    minimum_health_checks: int = Field(3, ge=1)
    rollback_delay_seconds: int = Field(30, ge=0)
    required_probe_types: Optional[str] = Field(None, max_length=100)
    minimum_successful_probes: int = Field(1, ge=1)
    probe_timeout_seconds: int = Field(10, ge=1)
    parallel_execution: bool = True
    promotion_stages: Dict[str, Any] = Field(default_factory=lambda: {"stages": [10, 25, 50, 75, 100]})
    required_consecutive_successes: int = Field(3, ge=1)


class DeploymentPolicyResponse(VersionedResponse):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    required_approvals: int
    required_reviewer_roles: Optional[str]
    maximum_latency_ms: Optional[float]
    maximum_error_rate: Optional[float]
    minimum_success_rate: Optional[float]
    minimum_throughput: Optional[float]
    minimum_health_checks: int
    rollback_delay_seconds: int
    required_probe_types: Optional[str]
    minimum_successful_probes: int
    probe_timeout_seconds: int
    parallel_execution: bool
    promotion_stages: Dict[str, Any]
    required_consecutive_successes: int
    policy_version: int
    is_active: bool
    superseded_by: Optional[uuid.UUID]
    created_by: Optional[uuid.UUID]
    created_at: datetime


# Deployments
class ModelDeploymentCreate(BaseModel):
    model_id: uuid.UUID
    environment_id: uuid.UUID
    strategy: str = Field(..., description="ROLLING, CANARY, BLUE_GREEN, SHADOW")
    deployment_version: str = Field(..., max_length=50)
    traffic_percentage: int = Field(100, ge=0, le=100)
    idempotency_key: Optional[str] = Field(None, max_length=128)
    variables: List[Dict[str, Any]] = []
    tags: Dict[str, str] = {}


class ModelDeploymentUpdate(BaseModel):
    status: Optional[str] = None
    traffic_percentage: Optional[int] = None


class ModelDeploymentResponse(VersionedResponse):
    id: uuid.UUID
    project_id: uuid.UUID
    model_id: uuid.UUID
    environment_id: uuid.UUID
    policy_version_id: uuid.UUID
    deployment_version: str
    status: str
    strategy: str
    traffic_percentage: int
    idempotency_key: Optional[str]
    version_number: int
    state_version: int
    created_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    # Artifact provenance
    artifact_repository: Optional[str] = None
    artifact_digest: Optional[str] = None
    artifact_size_bytes: Optional[int] = None
    artifact_created_at: Optional[datetime] = None
    artifact_signed_by: Optional[str] = None

    # Manifest meta
    manifest_version: Optional[str] = None
    manifest_checksum: Optional[str] = None
    manifest_schema_version: Optional[str] = None


# Manifest History
class DeploymentManifestHistoryResponse(VersionedResponse):
    id: uuid.UUID
    deployment_id: uuid.UUID
    manifest_version: str
    schema_version: str
    artifact_checksum: str
    model_checksum: str
    preprocessing_checksum: str
    training_checksum: str
    dataset_checksum: str
    python_version: str
    library_versions: Dict[str, Any]
    docker_image_digest: Optional[str]
    git_commit: Optional[str]
    manifest_signature: str
    generated_by: Optional[uuid.UUID]
    generated_at: datetime


# Checkpoint Response
class DeploymentCheckpointResponse(VersionedResponse):
    id: uuid.UUID
    deployment_id: uuid.UUID
    last_sequence_number: int
    checkpoint_hash: str
    schema_version: str
    compression: str
    hash_algorithm: str
    snapshot_size_bytes: int
    decompressed_size_bytes: int
    checkpoint_duration_ms: float
    created_by_instance: Optional[str]
    hash_algorithm_version: Optional[str]
    checkpoint_signature: Optional[str]
    signature_algorithm: Optional[str]
    signing_key_id: Optional[str]
    encryption_algorithm: Optional[str]
    encryption_key_version: Optional[str]
    created_at: datetime


# Replay Response
class ReplayResponse(VersionedResponse):
    status: str # FULLY_VERIFIED, PARTIALLY_VERIFIED, FALLBACK_REPLAY, NOT_VERIFIED
    verified_events: int
    verification_duration_ms: float
    fallback_reason: Optional[str] = None
    failure_class: Optional[str] = None
    details: Dict[str, Any] = {}


# Approvals
class DeploymentApprovalCreate(BaseModel):
    decision: str = Field(..., description="APPROVED, REJECTED")
    comments: Optional[str] = Field(None, max_length=255)


class DeploymentApprovalResponse(VersionedResponse):
    id: uuid.UUID
    deployment_id: uuid.UUID
    reviewer_id: uuid.UUID
    decision: str
    reviewer_order: int
    approval_stage: str
    comments: Optional[str]
    approval_duration_seconds: Optional[int]
    decided_at: datetime


# Health Logs
class DeploymentHealthLogCreate(BaseModel):
    cpu_usage_pct: float
    memory_usage_mb: float
    latency_ms: float
    throughput_rps: float
    error_count: int
    status: str
    deployment_duration_ms: int
    startup_time_ms: int
    container_ready_time: int
    traffic_shift_duration: int
    rollback_duration: int
    health_probe_count: int
    successful_probe_count: int
    failed_probe_count: int
    estimated_cpu_cost: float = 0.0
    estimated_memory_cost: float = 0.0
    estimated_runtime_cost: float = 0.0
    estimated_network_cost: float = 0.0


class DeploymentHealthLogResponse(VersionedResponse):
    id: uuid.UUID
    deployment_id: uuid.UUID
    recorded_at: datetime
    cpu_usage_pct: float
    memory_usage_mb: float
    latency_ms: float
    throughput_rps: float
    error_count: int
    status: str
    deployment_duration_ms: int
    startup_time_ms: int
    container_ready_time: int
    traffic_shift_duration: int
    rollback_duration: int
    health_probe_count: int
    successful_probe_count: int
    failed_probe_count: int
    estimated_cpu_cost: float
    estimated_memory_cost: float
    estimated_runtime_cost: float
    estimated_network_cost: float


class DeploymentHealthAggregatesResponse(VersionedResponse):
    deployment_id: uuid.UUID
    avg_cpu: float
    avg_memory: float
    avg_latency: float
    avg_throughput: float
    total_errors: int
    unhealthy_count: int


# Freeze Windows
class DeploymentFreezeWindowCreate(BaseModel):
    name: str = Field(..., max_length=100)
    start_day_of_week: int = Field(..., ge=0, le=6)
    start_time_utc: time
    end_day_of_week: int = Field(..., ge=0, le=6)
    end_time_utc: time


class DeploymentFreezeWindowResponse(VersionedResponse):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    start_day_of_week: int
    start_time_utc: time
    end_day_of_week: int
    end_time_utc: time
    is_active: bool
    created_at: datetime


# Environment Variables
class DeploymentEnvironmentVariableResponse(VersionedResponse):
    id: uuid.UUID
    deployment_id: uuid.UUID
    key: str
    secret_reference: Optional[str]
    scope: str
    required: bool
    created_at: datetime
