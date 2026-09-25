from fastapi import Depends

from app.repositories.interfaces.project_analytics import ProjectAnalyticsRepository
from app.repositories.interfaces.dataset_analytics import DatasetAnalyticsRepository
from app.repositories.interfaces.training_analytics import TrainingAnalyticsRepository
from app.repositories.interfaces.model_analytics import ModelAnalyticsRepository
from app.repositories.interfaces.comparison_analytics import ComparisonAnalyticsRepository

from app.repositories.mongodb.project_analytics import MongoProjectAnalyticsRepository
from app.repositories.mongodb.dataset_analytics import MongoDatasetAnalyticsRepository
from app.repositories.mongodb.training_analytics import MongoTrainingAnalyticsRepository
from app.repositories.mongodb.model_analytics import MongoModelAnalyticsRepository
from app.repositories.mongodb.comparison_analytics import MongoComparisonAnalyticsRepository

from app.services.analytics.cache import AnalyticsCache
from app.services.analytics.statistics import StatisticsService
from app.services.analytics.timeseries import TimeseriesService
from app.services.analytics.graph import LineageGraphService
from app.services.analytics.export import ExportService
from app.services.analytics.aggregation import AggregationService

from app.services.analytics.dashboard.dataset_dashboard import DatasetDashboardService
from app.services.analytics.dashboard.training_dashboard import TrainingDashboardService
from app.services.analytics.dashboard.model_dashboard import ModelDashboardService
from app.services.analytics.dashboard.activity_dashboard import ActivityDashboardService

# Singleton cache scope
_cache_instance = AnalyticsCache()


def get_project_analytics_repository() -> ProjectAnalyticsRepository:
    return MongoProjectAnalyticsRepository()


def get_dataset_analytics_repository() -> DatasetAnalyticsRepository:
    return MongoDatasetAnalyticsRepository()


def get_training_analytics_repository() -> TrainingAnalyticsRepository:
    return MongoTrainingAnalyticsRepository()


def get_model_analytics_repository() -> ModelAnalyticsRepository:
    return MongoModelAnalyticsRepository()


def get_comparison_analytics_repository() -> ComparisonAnalyticsRepository:
    return MongoComparisonAnalyticsRepository()


def get_analytics_cache() -> AnalyticsCache:
    return _cache_instance


def get_statistics_service() -> StatisticsService:
    return StatisticsService()


def get_timeseries_service() -> TimeseriesService:
    return TimeseriesService()


def get_lineage_graph_service() -> LineageGraphService:
    return LineageGraphService()


def get_export_service() -> ExportService:
    return ExportService()


def get_aggregation_service(
    project_repo: ProjectAnalyticsRepository = Depends(get_project_analytics_repository),
    dataset_repo: DatasetAnalyticsRepository = Depends(get_dataset_analytics_repository),
    training_repo: TrainingAnalyticsRepository = Depends(get_training_analytics_repository),
    model_repo: ModelAnalyticsRepository = Depends(get_model_analytics_repository),
) -> AggregationService:
    return AggregationService(project_repo, dataset_repo, training_repo, model_repo)


def get_dataset_dashboard_service(
    repo: DatasetAnalyticsRepository = Depends(get_dataset_analytics_repository)
) -> DatasetDashboardService:
    return DatasetDashboardService(repo)


def get_training_dashboard_service(
    repo: TrainingAnalyticsRepository = Depends(get_training_analytics_repository)
) -> TrainingDashboardService:
    return TrainingDashboardService(repo)


def get_model_dashboard_service(
    repo: ModelAnalyticsRepository = Depends(get_model_analytics_repository)
) -> ModelDashboardService:
    return ModelDashboardService(repo)


def get_activity_dashboard_service() -> ActivityDashboardService:
    return ActivityDashboardService()
