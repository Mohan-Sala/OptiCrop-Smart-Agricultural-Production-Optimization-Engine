from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.interfaces.project_analytics import ProjectAnalyticsRepository
from app.repositories.interfaces.dataset_analytics import DatasetAnalyticsRepository
from app.repositories.interfaces.training_analytics import TrainingAnalyticsRepository
from app.repositories.interfaces.model_analytics import ModelAnalyticsRepository
from app.repositories.interfaces.comparison_analytics import ComparisonAnalyticsRepository

from app.repositories.sqlalchemy.project_analytics import SqlAlchemyProjectAnalyticsRepository
from app.repositories.sqlalchemy.dataset_analytics import SqlAlchemyDatasetAnalyticsRepository
from app.repositories.sqlalchemy.training_analytics import SqlAlchemyTrainingAnalyticsRepository
from app.repositories.sqlalchemy.model_analytics import SqlAlchemyModelAnalyticsRepository
from app.repositories.sqlalchemy.comparison_analytics import SqlAlchemyComparisonAnalyticsRepository

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


def get_project_analytics_repository(db: AsyncSession = Depends(get_db)) -> ProjectAnalyticsRepository:
    return SqlAlchemyProjectAnalyticsRepository(db)


def get_dataset_analytics_repository(db: AsyncSession = Depends(get_db)) -> DatasetAnalyticsRepository:
    return SqlAlchemyDatasetAnalyticsRepository(db)


def get_training_analytics_repository(db: AsyncSession = Depends(get_db)) -> TrainingAnalyticsRepository:
    return SqlAlchemyTrainingAnalyticsRepository(db)


def get_model_analytics_repository(db: AsyncSession = Depends(get_db)) -> ModelAnalyticsRepository:
    return SqlAlchemyModelAnalyticsRepository(db)


def get_comparison_analytics_repository(db: AsyncSession = Depends(get_db)) -> ComparisonAnalyticsRepository:
    return SqlAlchemyComparisonAnalyticsRepository(db)


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


def get_activity_dashboard_service(db: AsyncSession = Depends(get_db)) -> ActivityDashboardService:
    return ActivityDashboardService(db)
