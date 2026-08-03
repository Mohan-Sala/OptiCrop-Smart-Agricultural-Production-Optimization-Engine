import uuid
from datetime import datetime, timezone, timedelta
from typing import List
from app.repositories.interfaces.alert import AlertRepository
from app.repositories.interfaces.drift import DriftRepository
from app.services.monitoring.health import HealthService
from app.services.monitoring.prediction_metrics import PredictionMetricsService
from app.schemas.monitoring import (
    MonitoringSnapshot,
    DiagnosticHealthDTO,
    AlertDTO,
    FeatureDriftMetadataDTO,
)
from app.core.enums import AlertStatus


class MonitoringDashboardService:
    """Prepares and compiles the unified MonitoringSnapshot DTO representing project monitoring overview."""

    def __init__(
        self,
        health_service: HealthService,
        metrics_service: PredictionMetricsService,
        alert_repo: AlertRepository,
        drift_repo: DriftRepository,
    ):
        self.health_service = health_service
        self.metrics_service = metrics_service
        self.alert_repo = alert_repo
        self.drift_repo = drift_repo

    async def compile_snapshot(self, project_id: uuid.UUID, model_id: uuid.UUID) -> MonitoringSnapshot:
        health_dto = await self.health_service.run_diagnostics()
        
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=30)
        metrics = await self.metrics_service.get_metrics(project_id, start, end)
        
        alerts = await self.alert_repo.list_alerts_by_project(project_id, AlertStatus.ACTIVE)
        active_alerts_dto = [
            AlertDTO(
                id=a.id,
                rule_name=a.rule_name,
                severity=a.severity,
                message=a.message,
                occurrence_count=a.occurrence_count,
                last_triggered_at=a.last_triggered_at,
                status=a.status,
                acknowledged_at=a.acknowledged_at,
                acknowledged_by=a.acknowledged_by,
                resolved_at=a.resolved_at,
                resolved_by=a.resolved_by,
            )
            for a in alerts
        ]
        
        drift = await self.drift_repo.get_latest_by_model(model_id)
        
        feature_drifts_dto = []
        overall_drift_score = 0.0
        is_drifted = False
        
        if drift and drift.feature_drifts:
            overall_drift_score = drift.drift_score
            is_drifted = drift.is_drifted
            for feat, details in drift.feature_drifts.items():
                feature_drifts_dto.append(
                    FeatureDriftMetadataDTO(
                        feature_name=details.get("feature_name", feat),
                        baseline_mean=details.get("baseline_mean", 0.0),
                        baseline_std=details.get("baseline_std", 1.0),
                        current_mean=details.get("current_mean", 0.0),
                        current_std=details.get("current_std", 1.0),
                        drift_score=details.get("drift_score", 0.0),
                        drift_detected=details.get("drift_detected", False),
                        importance_rank=details.get("importance_rank"),
                    )
                )

        return MonitoringSnapshot(
            project_id=project_id,
            model_id=model_id,
            prediction_count=metrics.get("total_predictions", 0),
            success_rate=metrics.get("success_rate", 100.0),
            cache_hit_ratio=metrics.get("cache_hit_ratio", 100.0),
            avg_latency_ms=metrics.get("avg_latency_ms", 0.0),
            health=health_dto,
            active_alerts=active_alerts_dto,
            feature_drifts=feature_drifts_dto,
            overall_drift_score=overall_drift_score,
            is_drifted=is_drifted,
        )
