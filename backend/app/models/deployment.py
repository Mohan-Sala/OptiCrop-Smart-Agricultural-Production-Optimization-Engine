import uuid
from datetime import datetime, time, timezone
from typing import Optional, Dict, Any
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class DeploymentEnvironment(AppDocument):
    project_id: uuid.UUID
    name: str
    is_production: bool = False
    description: Optional[str] = None

    class Settings:
        name = "deployment_environments"
        indexes = [
            IndexModel([("project_id", ASCENDING)]),
            IndexModel([("project_id", ASCENDING), ("name", ASCENDING)]),
        ]


class DeploymentSetting(AppDocument):
    project_id: uuid.UUID
    checkpoint_interval: int = 100
    checkpoint_retention_days: int = 30

    class Settings:
        name = "deployment_settings"
        indexes = [
            IndexModel([("project_id", ASCENDING)], unique=True),
        ]


class DeploymentPolicy(AppDocument):
    project_id: uuid.UUID
    name: str
    required_approvals: int = 1
    required_reviewer_roles: Optional[str] = None
    maximum_latency_ms: Optional[float] = None
    maximum_error_rate: Optional[float] = None
    minimum_success_rate: Optional[float] = None
    minimum_throughput: Optional[float] = None
    minimum_health_checks: int = 3
    rollback_delay_seconds: int = 30
    required_probe_types: Optional[str] = None
    minimum_successful_probes: int = 1
    probe_timeout_seconds: int = 10
    parallel_execution: bool = True
    promotion_stages: Dict[str, Any]  # e.g. [10, 25, 50, 75, 100]
    required_consecutive_successes: int = 3
    policy_version: int = 1
    is_active: bool = True
    superseded_by: Optional[uuid.UUID] = None
    created_by: Optional[uuid.UUID] = None
    policy_checksum: str

    class Settings:
        name = "deployment_policies"
        indexes = [
            IndexModel([("project_id", ASCENDING)]),
            IndexModel([("policy_version", ASCENDING)]),
            IndexModel([("is_active", ASCENDING)]),
        ]


class ModelDeployment(AppDocument):
    project_id: uuid.UUID
    model_id: uuid.UUID
    environment_id: uuid.UUID
    policy_version_id: uuid.UUID
    deployment_version: str
    status: str = "DRAFT"
    strategy: str
    traffic_percentage: int = 100
    idempotency_key: Optional[str] = None
    version_number: int = 1  # Optimistic locking
    state_version: int = 1   # Concurrency transitions state
    created_by: Optional[uuid.UUID] = None

    # Artifact Provenance
    artifact_repository: Optional[str] = None
    artifact_digest: Optional[str] = None
    artifact_size_bytes: Optional[int] = None
    artifact_created_at: Optional[datetime] = None
    artifact_signed_by: Optional[str] = None

    # Manifest metadata
    manifest_version: Optional[str] = None
    manifest_checksum: Optional[str] = None
    manifest_schema_version: Optional[str] = None

    class Settings:
        name = "model_deployments"
        indexes = [
            IndexModel([("project_id", ASCENDING)]),
            IndexModel([("model_id", ASCENDING)]),
            IndexModel([("environment_id", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("idempotency_key", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)]),
        ]


class DeploymentManifestHistory(AppDocument):
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
    docker_image_digest: Optional[str] = None
    git_commit: Optional[str] = None
    manifest_signature: str
    generated_by: Optional[uuid.UUID] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "deployment_manifest_history"
        indexes = [
            IndexModel([("deployment_id", ASCENDING)]),
            IndexModel([("manifest_version", ASCENDING)]),
        ]


class DeploymentEnvironmentVariable(AppDocument):
    deployment_id: uuid.UUID
    key: str
    encrypted_value: Optional[str] = None
    secret_reference: Optional[str] = None
    scope: str
    required: bool = False

    class Settings:
        name = "deployment_environment_variables"
        indexes = [
            IndexModel([("deployment_id", ASCENDING)]),
            IndexModel([("deployment_id", ASCENDING), ("key", ASCENDING)]),
        ]


class DeploymentVersion(AppDocument):
    deployment_id: uuid.UUID
    version_number: int
    model_version: int
    dataset_version: int
    preprocessing_version: int
    training_version: int
    prediction_version: int
    monitoring_version: int
    git_commit: Optional[str] = None
    docker_image_digest: Optional[str] = None
    artifact_checksum: str
    python_version: str
    library_versions: Dict[str, Any]
    status: str
    provider_name: Optional[str] = None
    provider_version: Optional[str] = None
    provider_capability_version: Optional[str] = None

    class Settings:
        name = "deployment_versions"
        indexes = [
            IndexModel([("deployment_id", ASCENDING)]),
            IndexModel([("deployment_id", ASCENDING), ("version_number", ASCENDING)]),
        ]


class DeploymentJobLock(AppDocument):
    environment_id: uuid.UUID
    lease_owner: uuid.UUID
    acquired_at: datetime
    heartbeat_at: datetime
    expires_at: datetime

    class Settings:
        name = "deployment_job_locks"
        indexes = [
            IndexModel([("environment_id", ASCENDING)], unique=True),
        ]


class DeploymentApproval(AppDocument):
    deployment_id: uuid.UUID
    reviewer_id: uuid.UUID
    decision: str  # APPROVED, REJECTED, PENDING
    reviewer_order: int = 1
    approval_stage: str
    comments: Optional[str] = None
    approval_duration_seconds: Optional[int] = None
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "deployment_approvals"
        indexes = [
            IndexModel([("deployment_id", ASCENDING)]),
            IndexModel([("reviewer_id", ASCENDING)]),
        ]


class DeploymentHealthLog(AppDocument):
    deployment_id: uuid.UUID
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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

    # Estimated costs
    estimated_cpu_cost: float = 0.0
    estimated_memory_cost: float = 0.0
    estimated_runtime_cost: float = 0.0
    estimated_network_cost: float = 0.0

    class Settings:
        name = "deployment_health_logs"
        indexes = [
            IndexModel([("deployment_id", ASCENDING)]),
            IndexModel([("recorded_at", ASCENDING)]),
        ]


class DeploymentEvent(AppDocument):
    deployment_id: Optional[uuid.UUID] = None
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_version: str = "v1"
    schema_version: str = "1.0"
    correlation_id: uuid.UUID
    trace_id: uuid.UUID
    event_type: str
    previous_state: Optional[str] = None
    new_state: str
    performed_by: Optional[uuid.UUID] = None
    reason: Optional[str] = None
    sequence_number: int
    event_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload_version: str = "1.0"
    replayable: bool = True
    previous_event_hash: Optional[str] = None
    current_event_hash: str

    class Settings:
        name = "deployment_events"
        indexes = [
            IndexModel([("deployment_id", ASCENDING)]),
            IndexModel([("correlation_id", ASCENDING)]),
            IndexModel([("trace_id", ASCENDING)]),
            IndexModel([("sequence_number", ASCENDING)]),
            IndexModel([("current_event_hash", ASCENDING)]),
            IndexModel([("event_timestamp", ASCENDING)]),
        ]


class DeploymentReplayMetric(AppDocument):
    deployment_id: uuid.UUID
    checkpoint_used: bool
    replay_source: str
    verification_duration_ms: float
    verified_events: int
    fallback_reason: Optional[str] = None
    failure_class: Optional[str] = None
    replay_confidence: str = "HIGH"
    
    # Extended metrics
    events_per_second: float = 0.0
    checkpoint_load_duration_ms: float = 0.0
    decompression_duration_ms: float = 0.0
    replay_duration_ms: float = 0.0

    class Settings:
        name = "deployment_replay_metrics"
        indexes = [
            IndexModel([("deployment_id", ASCENDING)]),
        ]


class DeploymentTag(AppDocument):
    deployment_id: uuid.UUID
    key: str
    value: str

    class Settings:
        name = "deployment_tags"
        indexes = [
            IndexModel([("deployment_id", ASCENDING)]),
            IndexModel([("key", ASCENDING)]),
        ]


class DeploymentEventCheckpoint(AppDocument):
    deployment_id: uuid.UUID
    last_sequence_number: int
    checkpoint_hash: str
    snapshot: bytes
    schema_version: str
    compression: str = "NONE"
    hash_algorithm: str = "SHA256"
    snapshot_size_bytes: int
    created_from_sequence: int = 0
    checkpoint_format_version: int = 1
    checkpoint_serializer: str = "JSON"
    serializer_version: Optional[str] = None
    backend_version: Optional[str] = None
    python_runtime: Optional[str] = None
    decompressed_size_bytes: int
    checkpoint_duration_ms: float
    created_by_instance: Optional[str] = None
    hash_algorithm_version: Optional[str] = None
    checkpoint_signature: Optional[str] = None
    signature_algorithm: Optional[str] = None
    signing_key_id: Optional[str] = None
    encryption_algorithm: Optional[str] = None
    encryption_key_version: Optional[str] = None

    class Settings:
        name = "deployment_event_checkpoints"
        indexes = [
            IndexModel([("deployment_id", ASCENDING)]),
            IndexModel([("last_sequence_number", ASCENDING)]),
            IndexModel([("checkpoint_hash", ASCENDING)]),
        ]


class DeploymentFreezeWindow(AppDocument):
    project_id: uuid.UUID
    name: str
    start_day_of_week: int  # 0 = Monday, 6 = Sunday
    start_time_utc: time
    end_day_of_week: int
    end_time_utc: time
    is_active: bool = True

    class Settings:
        name = "deployment_freeze_windows"
        indexes = [
            IndexModel([("project_id", ASCENDING)]),
            IndexModel([("is_active", ASCENDING)]),
        ]
        bson_encoders = {
            time: lambda t: t.isoformat() if hasattr(t, "isoformat") else str(t)
        }
