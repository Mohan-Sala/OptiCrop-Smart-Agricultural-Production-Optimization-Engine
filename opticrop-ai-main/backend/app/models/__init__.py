# app/models/__init__.py
from app.database.base import Base
from app.models.user import User
from app.models.project import Project
from app.models.dataset import Dataset
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.models.model_metric import ModelMetric
from app.models.prediction_history import PredictionHistory
from app.models.notification import Notification
from app.models.user_setting import UserSetting
from app.models.refresh_token import RefreshToken
from app.models.login_audit import LoginAudit
from app.models.dataset_statistics import DatasetStatistics
from app.models.dataset_preprocessing import DatasetPreprocessing
from app.models.preprocessing_artifact import PreprocessingArtifact
from app.models.feature_metadata import FeatureMetadata
from app.models.training_experiment import TrainingExperiment
from app.models.evaluation_report import EvaluationReport
from app.models.hyperparameter_set import HyperparameterSet
from app.models.prediction_run import PredictionRun, PredictionStatus
from app.models.monitoring_job_lock import MonitoringJobLock
from app.models.alert_rule import AlertRule
from app.models.monitoring_alert import MonitoringAlert
from app.models.drift_snapshot import DriftSnapshot
from app.models.monitoring_health_log import MonitoringHealthLog
from app.models.external_telemetry import ExternalTelemetryLog
from app.core.enums import AlertStatus, DriftStatus
from app.models.deployment import (
    DeploymentEnvironment,
    DeploymentSetting,
    DeploymentPolicy,
    ModelDeployment,
    DeploymentManifestHistory,
    DeploymentEnvironmentVariable,
    DeploymentVersion,
    DeploymentJobLock,
    DeploymentApproval,
    DeploymentHealthLog,
    DeploymentEvent,
    DeploymentReplayMetric,
    DeploymentTag,
    DeploymentEventCheckpoint,
    DeploymentFreezeWindow,
)

# Export all ORM metadata so it is discoverable by Alembic migrations
__all__ = [
    "Base",
    "User",
    "Project",
    "Dataset",
    "TrainingSession",
    "TrainedModel",
    "ModelMetric",
    "PredictionHistory",
    "Notification",
    "UserSetting",
    "RefreshToken",
    "LoginAudit",
    "DatasetStatistics",
    "DatasetPreprocessing",
    "PreprocessingArtifact",
    "FeatureMetadata",
    "TrainingExperiment",
    "EvaluationReport",
    "HyperparameterSet",
    "PredictionRun",
    "PredictionStatus",
    "MonitoringJobLock",
    "AlertRule",
    "MonitoringAlert",
    "DriftSnapshot",
    "MonitoringHealthLog",
    "ExternalTelemetryLog",
    "AlertStatus",
    "DriftStatus",
    "DeploymentEnvironment",
    "DeploymentSetting",
    "DeploymentPolicy",
    "ModelDeployment",
    "DeploymentManifestHistory",
    "DeploymentEnvironmentVariable",
    "DeploymentVersion",
    "DeploymentJobLock",
    "DeploymentApproval",
    "DeploymentHealthLog",
    "DeploymentEvent",
    "DeploymentReplayMetric",
    "DeploymentTag",
    "DeploymentEventCheckpoint",
    "DeploymentFreezeWindow",
]
