import uuid
import time
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.dependencies.auth import get_active_user
from app.dependencies.dataset import get_project_repository
from app.dependencies.deployment import (
    get_deployment_repository,
    get_checkpoint_manager,
    get_deployment_orchestrator,
    get_deployment_scheduler_service,
)
from app.models.deployment import (
    DeploymentEnvironment,
    DeploymentSetting,
    DeploymentPolicy,
    ModelDeployment,
    DeploymentApproval,
    DeploymentHealthLog,
    DeploymentFreezeWindow,
)
from app.schemas.deployment import (
    DeploymentEnvironmentCreate,
    DeploymentEnvironmentResponse,
    DeploymentSettingsUpdate,
    DeploymentSettingsResponse,
    DeploymentPolicyCreate,
    DeploymentPolicyResponse,
    ModelDeploymentCreate,
    ModelDeploymentUpdate,
    ModelDeploymentResponse,
    DeploymentApprovalCreate,
    DeploymentApprovalResponse,
    DeploymentHealthLogCreate,
    DeploymentHealthLogResponse,
    DeploymentHealthAggregatesResponse,
    DeploymentFreezeWindowCreate,
    DeploymentFreezeWindowResponse,
    DeploymentCheckpointResponse,
    ReplayResponse,
)
from app.services.deployment.exceptions import (
    DeploymentException,
    FreezeWindowActiveError,
    PolicyViolationError,
    IncompatibleProviderError,
    LockAcquisitionError,
    InvalidStateTransitionError,
)

router = APIRouter()

# Rate limiting state
max_parallel_replays = 5
max_replays_per_minute = 20

active_replays: List[str] = [] # list of active deployment IDs being replayed
replay_timestamps: List[float] = [] # timestamps of replays triggered in the last 60 seconds

def check_rate_limit(deployment_id: uuid.UUID):
    global replay_timestamps
    now = time.time()
    # prune old timestamps
    replay_timestamps = [t for t in replay_timestamps if now - t < 60]

    if len(active_replays) >= max_parallel_replays:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many parallel replays running. Please try again later."
        )

    if len(replay_timestamps) >= max_replays_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Too many replay requests per minute."
        )


# Environments
@router.post("/environments", response_model=DeploymentEnvironmentResponse, status_code=status.HTTP_201_CREATED)
async def create_environment(
    project_id: uuid.UUID,
    payload: DeploymentEnvironmentCreate,
    current_user = Depends(get_active_user),
    project_repo = Depends(get_project_repository),
    repo = Depends(get_deployment_repository),
):
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied.")

    env = DeploymentEnvironment(
        project_id=project_id,
        name=payload.name,
        is_production=payload.is_production,
        description=payload.description,
    )
    return await repo.create_environment(env)


@router.get("/environments", response_model=List[DeploymentEnvironmentResponse])
async def list_environments(
    project_id: uuid.UUID,
    current_user = Depends(get_active_user),
    project_repo = Depends(get_project_repository),
    repo = Depends(get_deployment_repository),
):
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied.")

    return await repo.list_environments(project_id)


# Policies
@router.post("/policies", response_model=DeploymentPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    project_id: uuid.UUID,
    payload: DeploymentPolicyCreate,
    current_user = Depends(get_active_user),
    project_repo = Depends(get_project_repository),
    repo = Depends(get_deployment_repository),
):
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied.")

    # Mark existing active policies as inactive
    active_policy = await repo.get_active_policy(project_id)
    if active_policy:
        active_policy.is_active = False

    # Compute mock policy checksum
    import hashlib
    h = hashlib.sha256()
    h.update(f"{project_id}-{payload.name}-{payload.required_approvals}".encode())
    checksum = h.hexdigest()

    policy = DeploymentPolicy(
        project_id=project_id,
        name=payload.name,
        required_approvals=payload.required_approvals,
        required_reviewer_roles=payload.required_reviewer_roles,
        maximum_latency_ms=payload.maximum_latency_ms,
        maximum_error_rate=payload.maximum_error_rate,
        minimum_success_rate=payload.minimum_success_rate,
        minimum_throughput=payload.minimum_throughput,
        minimum_health_checks=payload.minimum_health_checks,
        rollback_delay_seconds=payload.rollback_delay_seconds,
        required_probe_types=payload.required_probe_types,
        minimum_successful_probes=payload.minimum_successful_probes,
        probe_timeout_seconds=payload.probe_timeout_seconds,
        parallel_execution=payload.parallel_execution,
        promotion_stages=payload.promotion_stages,
        required_consecutive_successes=payload.required_consecutive_successes,
        is_active=True,
        created_by=current_user.id,
        policy_checksum=checksum,
    )
    return await repo.create_policy(policy)


@router.get("/policies/active", response_model=DeploymentPolicyResponse)
async def get_active_policy(
    project_id: uuid.UUID,
    current_user = Depends(get_active_user),
    project_repo = Depends(get_project_repository),
    repo = Depends(get_deployment_repository),
):
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied.")

    policy = await repo.get_active_policy(project_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active policy found.")
    return policy


# Deployments
@router.post("/", response_model=ModelDeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(
    project_id: uuid.UUID,
    payload: ModelDeploymentCreate,
    current_user = Depends(get_active_user),
    project_repo = Depends(get_project_repository),
    orchestrator = Depends(get_deployment_orchestrator),
):
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied.")

    try:
        return await orchestrator.create_deployment_record(
            project_id=project_id,
            model_id=payload.model_id,
            environment_id=payload.environment_id,
            strategy=payload.strategy,
            deployment_version=payload.deployment_version,
            user_id=current_user.id,
            idempotency_key=payload.idempotency_key,
            variables=payload.variables,
            tags=payload.tags,
        )
    except FreezeWindowActiveError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except IncompatibleProviderError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PolicyViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{id}", response_model=ModelDeploymentResponse)
async def get_deployment(
    id: uuid.UUID,
    current_user = Depends(get_active_user),
    repo = Depends(get_deployment_repository),
):
    deployment = await repo.get_deployment(id)
    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found.")
    return deployment


@router.post("/{id}/transition", response_model=ModelDeploymentResponse)
async def transition_deployment(
    id: uuid.UUID,
    next_state: str,
    expected_state_version: Optional[int] = None,
    current_user = Depends(get_active_user),
    orchestrator = Depends(get_deployment_orchestrator),
):
    try:
        return await orchestrator.transition_state(
            deployment_id=id,
            next_state=next_state,
            user_id=current_user.id,
            expected_state_version=expected_state_version,
        )
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PolicyViolationError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{id}/approvals", response_model=DeploymentApprovalResponse)
async def submit_approval(
    id: uuid.UUID,
    payload: DeploymentApprovalCreate,
    current_user = Depends(get_active_user),
    orchestrator = Depends(get_deployment_orchestrator),
):
    try:
        return await orchestrator.record_approval(
            deployment_id=id,
            reviewer_id=current_user.id,
            decision=payload.decision,
            comments=payload.comments,
        )
    except PolicyViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Replay Verification
@router.post("/{id}/replay", response_model=ReplayResponse)
async def trigger_replay(
    id: uuid.UUID,
    current_user = Depends(get_active_user),
    repo = Depends(get_deployment_repository),
    checkpoint_mgr = Depends(get_checkpoint_manager),
):
    # Enforce Rate Limiting
    check_rate_limit(id)

    # Register start of replay
    deployment_id_str = str(id)
    active_replays.append(deployment_id_str)
    replay_timestamps.append(time.time())

    try:
        deployment = await repo.get_deployment(id)
        if not deployment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found.")

        # Load events
        events = await repo.get_events(id)

        # Run verification and replay
        status_val, verified, duration_ms, fb_reason, fail_class, details = await checkpoint_mgr.verify_and_replay(
            deployment=deployment,
            events=events,
        )

        # Save metrics to database
        from app.models.deployment import DeploymentReplayMetric
        metric = DeploymentReplayMetric(
            deployment_id=id,
            checkpoint_used=(fb_reason != "NO_CHECKPOINT"),
            replay_source="CHECKPOINT_STORE",
            verification_duration_ms=duration_ms,
            verified_events=verified,
            fallback_reason=fb_reason,
            failure_class=fail_class,
            replay_confidence="HIGH" if status_val == "FULLY_VERIFIED" else "LOW",
            events_per_second=details.get("events_per_second", 0.0),
            checkpoint_load_duration_ms=details.get("checkpoint_load_duration_ms", 0.0),
            decompression_duration_ms=details.get("decompression_duration_ms", 0.0),
            replay_duration_ms=details.get("replay_duration_ms", 0.0),
        )
        await repo.create_replay_metric(metric)

        return ReplayResponse(
            status=status_val,
            verified_events=verified,
            verification_duration_ms=duration_ms,
            fallback_reason=fb_reason,
            failure_class=fail_class,
            details=details,
        )
    finally:
        if deployment_id_str in active_replays:
            active_replays.remove(deployment_id_str)


# Health Telemetry Logs
@router.post("/{id}/health-logs", response_model=DeploymentHealthLogResponse)
async def record_health_log(
    id: uuid.UUID,
    payload: DeploymentHealthLogCreate,
    current_user = Depends(get_active_user),
    repo = Depends(get_deployment_repository),
):
    deployment = await repo.get_deployment(id)
    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found.")

    log = DeploymentHealthLog(
        deployment_id=id,
        cpu_usage_pct=payload.cpu_usage_pct,
        memory_usage_mb=payload.memory_usage_mb,
        latency_ms=payload.latency_ms,
        throughput_rps=payload.throughput_rps,
        error_count=payload.error_count,
        status=payload.status,
        deployment_duration_ms=payload.deployment_duration_ms,
        startup_time_ms=payload.startup_time_ms,
        container_ready_time=payload.container_ready_time,
        traffic_shift_duration=payload.traffic_shift_duration,
        rollback_duration=payload.rollback_duration,
        health_probe_count=payload.health_probe_count,
        successful_probe_count=payload.successful_probe_count,
        failed_probe_count=payload.failed_probe_count,
        estimated_cpu_cost=payload.estimated_cpu_cost,
        estimated_memory_cost=payload.estimated_memory_cost,
        estimated_runtime_cost=payload.estimated_runtime_cost,
        estimated_network_cost=payload.estimated_network_cost,
    )
    return await repo.create_health_log(log)


@router.get("/{id}/health-logs/aggregate", response_model=DeploymentHealthAggregatesResponse)
async def get_health_aggregates(
    id: uuid.UUID,
    current_user = Depends(get_active_user),
    repo = Depends(get_deployment_repository),
):
    deployment = await repo.get_deployment(id)
    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found.")

    aggs = await repo.get_health_aggregates(id)
    return DeploymentHealthAggregatesResponse(
        deployment_id=id,
        avg_cpu=aggs["avg_cpu"],
        avg_memory=aggs["avg_memory"],
        avg_latency=aggs["avg_latency"],
        avg_throughput=aggs["avg_throughput"],
        total_errors=aggs["total_errors"],
        unhealthy_count=aggs["unhealthy_count"],
    )


# Freeze Windows
@router.post("/freeze-windows", response_model=DeploymentFreezeWindowResponse, status_code=status.HTTP_201_CREATED)
async def create_freeze_window(
    project_id: uuid.UUID,
    payload: DeploymentFreezeWindowCreate,
    current_user = Depends(get_active_user),
    project_repo = Depends(get_project_repository),
    repo = Depends(get_deployment_repository),
):
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied.")

    window = DeploymentFreezeWindow(
        project_id=project_id,
        name=payload.name,
        start_day_of_week=payload.start_day_of_week,
        start_time_utc=payload.start_time_utc,
        end_day_of_week=payload.end_day_of_week,
        end_time_utc=payload.end_time_utc,
        is_active=True,
    )
    return await repo.create_freeze_window(window)


@router.get("/freeze-windows", response_model=List[DeploymentFreezeWindowResponse])
async def list_freeze_windows(
    project_id: uuid.UUID,
    current_user = Depends(get_active_user),
    project_repo = Depends(get_project_repository),
    repo = Depends(get_deployment_repository),
):
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied.")

    return await repo.list_freeze_windows(project_id)


# Settings
@router.post("/settings", response_model=DeploymentSettingsResponse)
async def save_settings(
    project_id: uuid.UUID,
    payload: DeploymentSettingsUpdate,
    current_user = Depends(get_active_user),
    project_repo = Depends(get_project_repository),
    repo = Depends(get_deployment_repository),
):
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied.")

    settings_record = DeploymentSetting(
        project_id=project_id,
        checkpoint_interval=payload.checkpoint_interval,
        checkpoint_retention_days=payload.checkpoint_retention_days,
    )
    return await repo.save_settings(settings_record)


@router.get("/settings", response_model=DeploymentSettingsResponse)
async def get_settings(
    project_id: uuid.UUID,
    current_user = Depends(get_active_user),
    project_repo = Depends(get_project_repository),
    repo = Depends(get_deployment_repository),
):
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or access denied.")

    settings_record = await repo.get_settings(project_id)
    if not settings_record:
        # Return defaults
        settings_record = DeploymentSetting(
            project_id=project_id,
            checkpoint_interval=100,
            checkpoint_retention_days=30,
        )
    return settings_record
