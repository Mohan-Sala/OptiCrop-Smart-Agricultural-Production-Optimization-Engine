# app/repositories/__init__.py
# Re-exports abstract interfaces and concrete SQLAlchemy implementations for access consistency.

from app.repositories.interfaces.base import BaseRepository
from app.repositories.interfaces.user import UserRepository
from app.repositories.interfaces.project import ProjectRepository
from app.repositories.interfaces.dataset import DatasetRepository
from app.repositories.interfaces.training import TrainingRepository
from app.repositories.interfaces.prediction import PredictionRepository
from app.repositories.interfaces.prediction_history import PredictionHistoryRepository
from app.repositories.interfaces.prediction_audit import PredictionAuditRepository
from app.repositories.interfaces.notification import NotificationRepository
from app.repositories.interfaces.refresh_token import RefreshTokenRepository
from app.repositories.interfaces.login_audit import LoginAuditRepository
from app.repositories.interfaces.preprocessing import PreprocessingRepository
from app.repositories.interfaces.artifact import PreprocessingArtifactRepository
from app.repositories.interfaces.feature import FeatureMetadataRepository
from app.repositories.interfaces.experiment import ExperimentRepository
from app.repositories.interfaces.training_session import TrainingSessionRepository
from app.repositories.interfaces.trained_model import TrainedModelRepository
from app.repositories.interfaces.evaluation import EvaluationReportRepository
from app.repositories.interfaces.hyperparameter import HyperparameterSetRepository
from app.repositories.interfaces.project_analytics import ProjectAnalyticsRepository
from app.repositories.interfaces.dataset_analytics import DatasetAnalyticsRepository
from app.repositories.interfaces.training_analytics import TrainingAnalyticsRepository
from app.repositories.interfaces.model_analytics import ModelAnalyticsRepository
from app.repositories.interfaces.comparison_analytics import ComparisonAnalyticsRepository
from app.repositories.interfaces.health import HealthRepository
from app.repositories.interfaces.alert import AlertRepository
from app.repositories.interfaces.drift import DriftRepository
from app.repositories.interfaces.telemetry import TelemetryRepository
from app.repositories.interfaces.prediction_monitoring import PredictionMonitoringRepository
from app.repositories.interfaces.correlation import CorrelationRepository
from app.repositories.interfaces.deployment import DeploymentRepository

from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository
from app.repositories.sqlalchemy.user import SqlAlchemyUserRepository
from app.repositories.sqlalchemy.refresh_token import SqlAlchemyRefreshTokenRepository
from app.repositories.sqlalchemy.login_audit import SqlAlchemyLoginAuditRepository
from app.repositories.sqlalchemy.project import SqlAlchemyProjectRepository
from app.repositories.sqlalchemy.dataset import SqlAlchemyDatasetRepository
from app.repositories.sqlalchemy.preprocessing import SqlAlchemyPreprocessingRepository
from app.repositories.sqlalchemy.artifact import SqlAlchemyPreprocessingArtifactRepository
from app.repositories.sqlalchemy.feature import SqlAlchemyFeatureMetadataRepository
from app.repositories.sqlalchemy.experiment import SqlAlchemyExperimentRepository
from app.repositories.sqlalchemy.training_session import SqlAlchemyTrainingSessionRepository
from app.repositories.sqlalchemy.trained_model import SqlAlchemyTrainedModelRepository
from app.repositories.sqlalchemy.evaluation import SqlAlchemyEvaluationReportRepository
from app.repositories.sqlalchemy.hyperparameter import SqlAlchemyHyperparameterSetRepository
from app.repositories.sqlalchemy.project_analytics import SqlAlchemyProjectAnalyticsRepository
from app.repositories.sqlalchemy.dataset_analytics import SqlAlchemyDatasetAnalyticsRepository
from app.repositories.sqlalchemy.training_analytics import SqlAlchemyTrainingAnalyticsRepository
from app.repositories.sqlalchemy.model_analytics import SqlAlchemyModelAnalyticsRepository
from app.repositories.sqlalchemy.comparison_analytics import SqlAlchemyComparisonAnalyticsRepository
from app.repositories.sqlalchemy.prediction import SqlAlchemyPredictionRepository
from app.repositories.sqlalchemy.prediction_history import SqlAlchemyPredictionHistoryRepository
from app.repositories.sqlalchemy.prediction_audit import SqlAlchemyPredictionAuditRepository
from app.repositories.sqlalchemy.health import SqlAlchemyHealthRepository
from app.repositories.sqlalchemy.alert import SqlAlchemyAlertRepository
from app.repositories.sqlalchemy.drift import SqlAlchemyDriftRepository
from app.repositories.sqlalchemy.telemetry import SqlAlchemyTelemetryRepository
from app.repositories.sqlalchemy.prediction_monitoring import SqlAlchemyPredictionMonitoringRepository
from app.repositories.sqlalchemy.correlation import SqlAlchemyCorrelationRepository
from app.repositories.sqlalchemy.deployment import SqlAlchemyDeploymentRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "ProjectRepository",
    "DatasetRepository",
    "TrainingRepository",
    "PredictionRepository",
    "PredictionHistoryRepository",
    "PredictionAuditRepository",
    "NotificationRepository",
    "RefreshTokenRepository",
    "LoginAuditRepository",
    "PreprocessingRepository",
    "PreprocessingArtifactRepository",
    "FeatureMetadataRepository",
    "ExperimentRepository",
    "TrainingSessionRepository",
    "TrainedModelRepository",
    "EvaluationReportRepository",
    "HyperparameterSetRepository",
    "ProjectAnalyticsRepository",
    "DatasetAnalyticsRepository",
    "TrainingAnalyticsRepository",
    "ModelAnalyticsRepository",
    "ComparisonAnalyticsRepository",
    "HealthRepository",
    "AlertRepository",
    "DriftRepository",
    "TelemetryRepository",
    "PredictionMonitoringRepository",
    "CorrelationRepository",
    "DeploymentRepository",
    "SqlAlchemyBaseRepository",
    "SqlAlchemyUserRepository",
    "SqlAlchemyRefreshTokenRepository",
    "SqlAlchemyLoginAuditRepository",
    "SqlAlchemyProjectRepository",
    "SqlAlchemyDatasetRepository",
    "SqlAlchemyPreprocessingRepository",
    "SqlAlchemyPreprocessingArtifactRepository",
    "SqlAlchemyFeatureMetadataRepository",
    "SqlAlchemyExperimentRepository",
    "SqlAlchemyTrainingSessionRepository",
    "SqlAlchemyTrainedModelRepository",
    "SqlAlchemyEvaluationReportRepository",
    "SqlAlchemyHyperparameterSetRepository",
    "SqlAlchemyProjectAnalyticsRepository",
    "SqlAlchemyDatasetAnalyticsRepository",
    "SqlAlchemyTrainingAnalyticsRepository",
    "SqlAlchemyModelAnalyticsRepository",
    "SqlAlchemyComparisonAnalyticsRepository",
    "SqlAlchemyPredictionRepository",
    "SqlAlchemyPredictionHistoryRepository",
    "SqlAlchemyPredictionAuditRepository",
    "SqlAlchemyHealthRepository",
    "SqlAlchemyAlertRepository",
    "SqlAlchemyDriftRepository",
    "SqlAlchemyTelemetryRepository",
    "SqlAlchemyPredictionMonitoringRepository",
    "SqlAlchemyCorrelationRepository",
    "SqlAlchemyDeploymentRepository",
]
