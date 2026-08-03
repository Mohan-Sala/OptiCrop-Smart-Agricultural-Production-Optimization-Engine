import uuid
from datetime import datetime, time
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Uuid, JSON, Integer, Float, Time, LargeBinary, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database.base import Base, AuditMixin

class DeploymentEnvironment(Base, AuditMixin):
    __tablename__ = "deployment_environments"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_production: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    deployments: Mapped[List["ModelDeployment"]] = relationship(
        "ModelDeployment", back_populates="environment", cascade="all, delete-orphan"
    )


class DeploymentSetting(Base):
    __tablename__ = "deployment_settings"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    checkpoint_interval: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    checkpoint_retention_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project")


class DeploymentPolicy(Base, AuditMixin):
    __tablename__ = "deployment_policies"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    required_approvals: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    required_reviewer_roles: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    maximum_latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    maximum_error_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    minimum_success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    minimum_throughput: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    minimum_health_checks: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    rollback_delay_seconds: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    required_probe_types: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    minimum_successful_probes: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    probe_timeout_seconds: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    parallel_execution: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    promotion_stages: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False) # e.g. [10, 25, 50, 75, 100]
    required_consecutive_successes: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    policy_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    superseded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("deployment_policies.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    policy_checksum: Mapped[str] = mapped_column(String(64), nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    creator: Mapped[Optional["User"]] = relationship("User")


class ModelDeployment(Base, AuditMixin):
    __tablename__ = "model_deployments"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("trained_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    environment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("deployment_environments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    policy_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("deployment_policies.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    deployment_version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False, index=True)
    strategy: Mapped[str] = mapped_column(String(30), nullable=False)
    traffic_percentage: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False) # Optimistic locking
    state_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)   # Concurrency transitions state
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Artifact Provenance
    artifact_repository: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    artifact_digest: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    artifact_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    artifact_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    artifact_signed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Manifest metadata
    manifest_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    manifest_checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    manifest_schema_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    model: Mapped["TrainedModel"] = relationship("TrainedModel")
    environment: Mapped["DeploymentEnvironment"] = relationship("DeploymentEnvironment", back_populates="deployments")
    policy_version: Mapped["DeploymentPolicy"] = relationship("DeploymentPolicy")
    creator_user: Mapped[Optional["User"]] = relationship("User")

    manifest_history: Mapped[List["DeploymentManifestHistory"]] = relationship(
        "DeploymentManifestHistory", back_populates="deployment", cascade="all, delete-orphan"
    )
    environment_variables: Mapped[List["DeploymentEnvironmentVariable"]] = relationship(
        "DeploymentEnvironmentVariable", back_populates="deployment", cascade="all, delete-orphan"
    )
    versions: Mapped[List["DeploymentVersion"]] = relationship(
        "DeploymentVersion", back_populates="deployment", cascade="all, delete-orphan"
    )
    approvals: Mapped[List["DeploymentApproval"]] = relationship(
        "DeploymentApproval", back_populates="deployment", cascade="all, delete-orphan"
    )
    health_logs: Mapped[List["DeploymentHealthLog"]] = relationship(
        "DeploymentHealthLog", back_populates="deployment", cascade="all, delete-orphan"
    )
    events: Mapped[List["DeploymentEvent"]] = relationship(
        "DeploymentEvent", back_populates="deployment", cascade="all, delete-orphan"
    )
    replay_metrics: Mapped[List["DeploymentReplayMetric"]] = relationship(
        "DeploymentReplayMetric", back_populates="deployment", cascade="all, delete-orphan"
    )
    tags: Mapped[List["DeploymentTag"]] = relationship(
        "DeploymentTag", back_populates="deployment", cascade="all, delete-orphan"
    )
    checkpoints: Mapped[List["DeploymentEventCheckpoint"]] = relationship(
        "DeploymentEventCheckpoint", back_populates="deployment", cascade="all, delete-orphan"
    )


class DeploymentManifestHistory(Base):
    __tablename__ = "deployment_manifest_history"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("model_deployments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    manifest_version: Mapped[str] = mapped_column(String(20), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(20), nullable=False)
    artifact_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    model_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    preprocessing_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    training_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    dataset_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    python_version: Mapped[str] = mapped_column(String(20), nullable=False)
    library_versions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    docker_image_digest: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    git_commit: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    manifest_signature: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    deployment: Mapped["ModelDeployment"] = relationship("ModelDeployment", back_populates="manifest_history")
    user: Mapped[Optional["User"]] = relationship("User")


class DeploymentEnvironmentVariable(Base):
    __tablename__ = "deployment_environment_variables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("model_deployments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    encrypted_value: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    secret_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    deployment: Mapped["ModelDeployment"] = relationship("ModelDeployment", back_populates="environment_variables")


class DeploymentVersion(Base):
    __tablename__ = "deployment_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("model_deployments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    model_version: Mapped[int] = mapped_column(Integer, nullable=False)
    dataset_version: Mapped[int] = mapped_column(Integer, nullable=False)
    preprocessing_version: Mapped[int] = mapped_column(Integer, nullable=False)
    training_version: Mapped[int] = mapped_column(Integer, nullable=False)
    prediction_version: Mapped[int] = mapped_column(Integer, nullable=False)
    monitoring_version: Mapped[int] = mapped_column(Integer, nullable=False)
    git_commit: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    docker_image_digest: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    artifact_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    python_version: Mapped[str] = mapped_column(String(20), nullable=False)
    library_versions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    provider_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    provider_capability_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    deployment: Mapped["ModelDeployment"] = relationship("ModelDeployment", back_populates="versions")


class DeploymentJobLock(Base):
    __tablename__ = "deployment_job_locks"

    environment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("deployment_environments.id", ondelete="CASCADE"), primary_key=True
    )
    lease_owner: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    heartbeat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DeploymentApproval(Base):
    __tablename__ = "deployment_approvals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("model_deployments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    decision: Mapped[str] = mapped_column(String(20), nullable=False) # APPROVED, REJECTED, PENDING
    reviewer_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    approval_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    comments: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approval_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    deployment: Mapped["ModelDeployment"] = relationship("ModelDeployment", back_populates="approvals")
    reviewer: Mapped["User"] = relationship("User")


class DeploymentHealthLog(Base):
    __tablename__ = "deployment_health_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("model_deployments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    cpu_usage_pct: Mapped[float] = mapped_column(Float, nullable=False)
    memory_usage_mb: Mapped[float] = mapped_column(Float, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    throughput_rps: Mapped[float] = mapped_column(Float, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    deployment_duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    startup_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    container_ready_time: Mapped[int] = mapped_column(Integer, nullable=False)
    traffic_shift_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    rollback_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    health_probe_count: Mapped[int] = mapped_column(Integer, nullable=False)
    successful_probe_count: Mapped[int] = mapped_column(Integer, nullable=False)
    failed_probe_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Estimated costs
    estimated_cpu_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estimated_memory_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estimated_runtime_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estimated_network_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    deployment: Mapped["ModelDeployment"] = relationship("ModelDeployment", back_populates="health_logs")


class DeploymentEvent(Base):
    __tablename__ = "deployment_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("model_deployments.id", ondelete="CASCADE"), nullable=True, index=True
    )
    event_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), default=uuid.uuid4, nullable=False)
    event_version: Mapped[str] = mapped_column(String(10), default="v1", nullable=False)
    schema_version: Mapped[str] = mapped_column(String(10), default="1.0", nullable=False)
    correlation_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    trace_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_state: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    new_state: Mapped[str] = mapped_column(String(30), nullable=False)
    performed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    payload_version: Mapped[str] = mapped_column(String(10), default="1.0", nullable=False)
    replayable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    previous_event_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    current_event_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    deployment: Mapped[Optional["ModelDeployment"]] = relationship("ModelDeployment", back_populates="events")
    user: Mapped[Optional["User"]] = relationship("User")


class DeploymentReplayMetric(Base):
    __tablename__ = "deployment_replay_metrics"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("model_deployments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    checkpoint_used: Mapped[bool] = mapped_column(Boolean, nullable=False)
    replay_source: Mapped[str] = mapped_column(String(50), nullable=False)
    verification_duration_ms: Mapped[float] = mapped_column(Float, nullable=False)
    verified_events: Mapped[int] = mapped_column(Integer, nullable=False)
    fallback_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    failure_class: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    replay_confidence: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    
    # Extended metrics
    events_per_second: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    checkpoint_load_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    decompression_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    replay_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    deployment: Mapped["ModelDeployment"] = relationship("ModelDeployment", back_populates="replay_metrics")


class DeploymentTag(Base):
    __tablename__ = "deployment_tags"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("model_deployments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Relationships
    deployment: Mapped["ModelDeployment"] = relationship("ModelDeployment", back_populates="tags")


class DeploymentEventCheckpoint(Base):
    __tablename__ = "deployment_event_checkpoints"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deployment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("model_deployments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    last_sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    checkpoint_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    snapshot: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    schema_version: Mapped[str] = mapped_column(String(20), nullable=False)
    compression: Mapped[str] = mapped_column(String(20), default="NONE", nullable=False)
    hash_algorithm: Mapped[str] = mapped_column(String(20), default="SHA256", nullable=False)
    snapshot_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_from_sequence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    checkpoint_format_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    checkpoint_serializer: Mapped[str] = mapped_column(String(30), default="JSON", nullable=False)
    serializer_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    backend_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    python_runtime: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    decompressed_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checkpoint_duration_ms: Mapped[float] = mapped_column(Float, nullable=False)
    created_by_instance: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hash_algorithm_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    checkpoint_signature: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    signature_algorithm: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    signing_key_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    encryption_algorithm: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    encryption_key_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    deployment: Mapped["ModelDeployment"] = relationship("ModelDeployment", back_populates="checkpoints")


class DeploymentFreezeWindow(Base):
    __tablename__ = "deployment_freeze_windows"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_day_of_week: Mapped[int] = mapped_column(Integer, nullable=False) # 0 = Monday, 6 = Sunday
    start_time_utc: Mapped[time] = mapped_column(Time, nullable=False)
    end_day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    end_time_utc: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project")
