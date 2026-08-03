from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.interfaces.health import HealthRepository
from app.repositories.interfaces.alert import AlertRepository
from app.repositories.interfaces.drift import DriftRepository
from app.repositories.interfaces.telemetry import TelemetryRepository
from app.repositories.interfaces.prediction_monitoring import PredictionMonitoringRepository
from app.repositories.interfaces.correlation import CorrelationRepository
from app.repositories.interfaces.trained_model import TrainedModelRepository
from app.repositories.interfaces.prediction import PredictionRepository

from app.repositories.sqlalchemy.health import SqlAlchemyHealthRepository
from app.repositories.sqlalchemy.alert import SqlAlchemyAlertRepository
from app.repositories.sqlalchemy.drift import SqlAlchemyDriftRepository
from app.repositories.sqlalchemy.telemetry import SqlAlchemyTelemetryRepository
from app.repositories.sqlalchemy.prediction_monitoring import SqlAlchemyPredictionMonitoringRepository
from app.repositories.sqlalchemy.correlation import SqlAlchemyCorrelationRepository
from app.dependencies.training import get_trained_model_repository
from app.dependencies.prediction import get_prediction_repository

from app.services.monitoring.event_bus import InProcessEventBus
from app.services.monitoring.cache import MonitoringCache
from app.services.monitoring.drift_algorithms import DriftAlgorithmRegistry
from app.services.monitoring.telemetry_plugins import TelemetryProviderRegistry
from app.services.monitoring.correlation import CorrelationService
from app.services.monitoring.health import HealthService
from app.services.monitoring.alerts import AlertsService
from app.services.monitoring.drift import DriftService
from app.services.monitoring.prediction_metrics import PredictionMetricsService
from app.services.monitoring.export import MonitoringExportService
from app.services.monitoring.dashboard import MonitoringDashboardService
from app.services.monitoring.timeseries import TimeSeriesAggregationService

# Singletons registrations
_event_bus_instance = InProcessEventBus()
_monitoring_cache_instance = MonitoringCache(_event_bus_instance)
_drift_algo_registry_instance = DriftAlgorithmRegistry()
_telemetry_provider_registry_instance = TelemetryProviderRegistry()


def get_health_repository(db: AsyncSession = Depends(get_db)) -> HealthRepository:
    return SqlAlchemyHealthRepository(db)


def get_alert_repository(db: AsyncSession = Depends(get_db)) -> AlertRepository:
    return SqlAlchemyAlertRepository(db)


def get_drift_repository(db: AsyncSession = Depends(get_db)) -> DriftRepository:
    return SqlAlchemyDriftRepository(db)


def get_telemetry_repository(db: AsyncSession = Depends(get_db)) -> TelemetryRepository:
    return SqlAlchemyTelemetryRepository(db)


def get_prediction_monitoring_repository(db: AsyncSession = Depends(get_db)) -> PredictionMonitoringRepository:
    return SqlAlchemyPredictionMonitoringRepository(db)


def get_correlation_repository(db: AsyncSession = Depends(get_db)) -> CorrelationRepository:
    return SqlAlchemyCorrelationRepository(db)


def get_event_bus() -> InProcessEventBus:
    return _event_bus_instance


def get_monitoring_cache() -> MonitoringCache:
    return _monitoring_cache_instance


def get_drift_algorithm_registry() -> DriftAlgorithmRegistry:
    return _drift_algo_registry_instance


def get_telemetry_provider_registry() -> TelemetryProviderRegistry:
    return _telemetry_provider_registry_instance


def get_health_service(
    health_repo: HealthRepository = Depends(get_health_repository)
) -> HealthService:
    return HealthService(health_repo)


def get_alerts_service(
    alert_repo: AlertRepository = Depends(get_alert_repository)
) -> AlertsService:
    return AlertsService(alert_repo)


def get_drift_service(
    drift_repo: DriftRepository = Depends(get_drift_repository),
    model_repo: TrainedModelRepository = Depends(get_trained_model_repository),
    pred_repo: PredictionRepository = Depends(get_prediction_repository),
    algo_registry: DriftAlgorithmRegistry = Depends(get_drift_algorithm_registry),
) -> DriftService:
    return DriftService(drift_repo, model_repo, pred_repo, algo_registry)


def get_prediction_metrics_service(
    metrics_repo: PredictionMonitoringRepository = Depends(get_prediction_monitoring_repository)
) -> PredictionMetricsService:
    return PredictionMetricsService(metrics_repo)


def get_correlation_service(
    correlation_repo: CorrelationRepository = Depends(get_correlation_repository)
) -> CorrelationService:
    return CorrelationService(correlation_repo)


def get_monitoring_export_service() -> MonitoringExportService:
    return MonitoringExportService()


def get_monitoring_dashboard_service(
    health_s: HealthService = Depends(get_health_service),
    metrics_s: PredictionMetricsService = Depends(get_prediction_metrics_service),
    alert_repo: AlertRepository = Depends(get_alert_repository),
    drift_repo: DriftRepository = Depends(get_drift_repository),
) -> MonitoringDashboardService:
    return MonitoringDashboardService(health_s, metrics_s, alert_repo, drift_repo)


def get_timeseries_aggregation_service(
    metrics_repo: PredictionMonitoringRepository = Depends(get_prediction_monitoring_repository)
) -> TimeSeriesAggregationService:
    return TimeSeriesAggregationService(metrics_repo)
