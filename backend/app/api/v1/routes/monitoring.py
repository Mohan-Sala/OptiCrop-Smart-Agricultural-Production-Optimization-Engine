import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Header, BackgroundTasks, status

from app.dependencies.auth import get_active_user
from app.dependencies.dataset import get_project_repository
from app.dependencies.training import get_trained_model_repository
from app.dependencies.monitoring import (
    get_alert_repository,
    get_drift_repository,
    get_telemetry_repository,
    get_health_service,
    get_alerts_service,
    get_drift_service,
    get_prediction_metrics_service,
    get_correlation_service,
    get_monitoring_export_service,
    get_monitoring_dashboard_service,
    get_timeseries_aggregation_service,
    get_telemetry_provider_registry,
    get_monitoring_cache,
    get_event_bus,
)
from app.schemas.monitoring import (
    HealthResponse,
    MonitoringOverviewResponse,
    MonitoringSnapshot,
    DriftResponse,
    ExternalTelemetryIngestRequest,
    MonitoringExportResponse,
    AlertRuleCreate,
    AlertRuleResponse,
)
from app.models.alert_rule import AlertRule
from app.models.external_telemetry import ExternalTelemetryLog
from app.utils.exceptions import NotFoundException, ValidationException

router = APIRouter()


# --- 1. HEALTH ENGINE ---

@router.get("/health", response_model=HealthResponse)
async def get_monitoring_health(
    current_user=Depends(get_active_user),
    health_s=Depends(get_health_service),
):
    """Diagnoses connection status of DB, cache, scheduler, storage, and event bus."""
    health_dto = await health_s.run_diagnostics()
    return HealthResponse(
        status=health_dto.overall_status,
        health_details=health_dto
    )


# --- 2. OVERVIEW APIs ---

@router.get("/overview", response_model=MonitoringOverviewResponse)
async def get_monitoring_overview(
    current_user=Depends(get_active_user),
    cache=Depends(get_monitoring_cache),
    metrics_s=Depends(get_prediction_metrics_service),
    alert_repo=Depends(get_alert_repository),
    project_repo=Depends(get_project_repository),
):
    """Aggregates latency averages, total prediction counts, success rates across user projects."""
    cached_val = cache.get("monitoring:overview")
    if cached_val:
        return cached_val

    projects = await project_repo.get_by_user_id(current_user.id)
    total_runs = 0
    failures = 0
    total_latency_sum = 0.0
    active_alerts = 0

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=30)

    for p in projects:
        metrics = await metrics_s.get_metrics(p.id, start, end)
        total_runs += metrics.get("total_predictions", 0)
        failures += metrics.get("failures_count", 0)
        total_latency_sum += metrics.get("avg_latency_ms", 0.0) * metrics.get("total_predictions", 0)
        
        alerts = await alert_repo.list_alerts_by_project(p.id, "ACTIVE")
        active_alerts += len(alerts)

    avg_latency = total_latency_sum / total_runs if total_runs > 0 else 0.0
    success_rate = ((total_runs - failures) / total_runs) * 100.0 if total_runs > 0 else 100.0

    resp = MonitoringOverviewResponse(
        total_predictions=total_runs,
        success_rate=round(success_rate, 2),
        avg_latency_ms=round(avg_latency, 2),
        active_alerts_count=active_alerts,
        active_models_count=len(projects),
    )
    cache.set("monitoring:overview", resp)
    return resp


# --- 3. PROJECT DIAGNOSTICS SNAPSHOTS ---

@router.get("/project/{project_id}", response_model=MonitoringSnapshot)
async def get_project_monitoring_snapshot(
    project_id: uuid.UUID,
    model_id: uuid.UUID,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    dashboard_s=Depends(get_monitoring_dashboard_service),
):
    """Returns a unified MonitoringSnapshot DTO combining cache rates, health state, and drift snapshots."""
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found.")

    return await dashboard_s.compile_snapshot(project_id, model_id)


# --- 4. DATA DRIFT DIAGNOSTICS ---

@router.get("/drift/{model_id}", response_model=DriftResponse)
async def check_model_drift(
    model_id: uuid.UUID,
    algorithm: str = Query("PSI"),
    current_user=Depends(get_active_user),
    trained_model_repo=Depends(get_trained_model_repository),
    project_repo=Depends(get_project_repository),
    drift_s=Depends(get_drift_service),
):
    """Triggers and returns extensible population drift statistics calculations."""
    model = await trained_model_repo.get_by_id(model_id)
    if not model:
        raise NotFoundException("Model not found.")
        
    session_rec = model.training_session
    dataset = session_rec.dataset
    project = await project_repo.get_by_id_and_user_id(dataset.project_id, current_user.id)
    if not project:
        raise NotFoundException("Access denied.")

    snapshot = await drift_s.calculate_drift(model_id, algorithm)
    
    feature_drifts_dto = []
    for feat, details in snapshot.feature_drifts.items():
        from app.schemas.monitoring import FeatureDriftMetadataDTO
        feature_drifts_dto.append(
            FeatureDriftMetadataDTO(
                feature_name=feat,
                baseline_mean=details.get("baseline_mean", 0.0),
                baseline_std=details.get("baseline_std", 1.0),
                current_mean=details.get("current_mean", 0.0),
                current_std=details.get("current_std", 1.0),
                drift_score=details.get("drift_score", 0.0),
                drift_detected=details.get("drift_detected", False),
            )
        )

    return DriftResponse(
        model_id=model_id,
        overall_drift_score=snapshot.drift_score,
        is_drifted=snapshot.is_drifted,
        status=snapshot.status,
        feature_drifts=feature_drifts_dto,
        target_drift=snapshot.target_drift,
        error_message=snapshot.error_message,
    )


# --- 5. TELEMETRY INGESTION ---

@router.post("/telemetry/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_external_telemetry(
    project_id: uuid.UUID,
    payload: ExternalTelemetryIngestRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    telemetry_repo=Depends(get_telemetry_repository),
    provider_registry=Depends(get_telemetry_provider_registry),
    event_bus=Depends(get_event_bus),
):
    """Validates, normalizes, and persists drone/sensor environmental telemetry, raising events asynchronously."""
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found.")

    try:
        provider = provider_registry.get(payload.provider_name)
    except KeyError:
        raise ValidationException(f"Unsupported telemetry provider: '{payload.provider_name}'")

    # Validate and normalize
    provider.validate(payload.payload)
    normalized = provider.normalize(payload.payload)

    # Save to db
    log_record = ExternalTelemetryLog(
        project_id=project_id,
        provider_name=payload.provider_name,
        source_id=payload.source_id,
        provider_record_id=payload.provider_record_id,
        ingestion_status="NORMALIZED",
        recorded_at=payload.recorded_at,
        normalized_payload=normalized,
    )
    await telemetry_repo.create(log_record)
    await telemetry_repo.session.flush()
    await telemetry_repo.session.commit()

    # Trigger async event notification
    background_tasks.add_task(
        event_bus.publish,
        "TelemetryIngested",
        {"project_id": str(project_id), "provider": payload.provider_name}
    )
    
    return {"message": "Telemetry ingestion succeeded.", "record_id": log_record.id}


# --- 6. ALERT RULES CONFIGURATIONS ---

@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    project_id: uuid.UUID,
    payload: AlertRuleCreate,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    alert_repo=Depends(get_alert_repository),
):
    """Configures thresholds for monitoring alert evaluations."""
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found.")

    rule = AlertRule(
        project_id=project_id,
        metric_name=payload.metric_name,
        threshold_value=payload.threshold_value,
        comparison_operator=payload.comparison_operator,
        is_active=payload.is_active,
    )
    await alert_repo.create_rule(rule)
    await alert_repo.session.commit()

    return AlertRuleResponse(
        id=rule.id,
        project_id=rule.project_id,
        metric_name=rule.metric_name,
        threshold_value=rule.threshold_value,
        comparison_operator=rule.comparison_operator,
        is_active=rule.is_active,
        created_at=rule.created_at,
    )


# --- 7. EXPORTS ---

@router.get("/export/{export_format}", response_model=MonitoringExportResponse)
async def export_monitoring_history(
    export_format: str,
    project_id: uuid.UUID,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    alert_repo=Depends(get_alert_repository),
    export_s=Depends(get_monitoring_export_service),
):
    """Exports active telemetry alarms history to JSON/CSV downloadable content strings."""
    if export_format.lower() not in ["json", "csv"]:
        raise ValidationException("Supported export formats: 'json', 'csv'.")

    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found.")

    alerts = await alert_repo.list_alerts_by_project(project_id)
    flat = []
    for a in alerts:
        flat.append({
            "id": str(a.id),
            "rule_name": a.rule_name,
            "severity": a.severity,
            "message": a.message,
            "metric_value": a.metric_value,
            "threshold_value": a.threshold_value,
            "status": a.status,
        })

    if export_format.lower() == "json":
        content = export_s.to_json(flat)
    else:
        content = export_s.to_csv(flat)

    return MonitoringExportResponse(
        project_id=project_id,
        export_format=export_format,
        content=content,
        filename=f"opticrop_monitoring_{project_id}.{export_format}",
    )
