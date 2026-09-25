from fastapi import Depends

from app.repositories.interfaces.dataset import DatasetRepository
from app.repositories.interfaces.experiment import ExperimentRepository
from app.repositories.interfaces.training_session import TrainingSessionRepository
from app.repositories.interfaces.trained_model import TrainedModelRepository
from app.repositories.interfaces.evaluation import EvaluationReportRepository
from app.repositories.interfaces.hyperparameter import HyperparameterSetRepository

from app.repositories.mongodb.experiment import MongoExperimentRepository
from app.repositories.mongodb.training_session import MongoTrainingSessionRepository
from app.repositories.mongodb.trained_model import MongoTrainedModelRepository
from app.repositories.mongodb.evaluation import MongoEvaluationReportRepository
from app.repositories.mongodb.hyperparameter import MongoHyperparameterSetRepository

from app.services.dataset.storage import StorageService
from app.dependencies.dataset import get_dataset_repository, get_storage_service

from app.services.training.training import TrainingService
from app.services.training.evaluation import EvaluationService
from app.services.training.comparison import ComparisonService
from app.services.training.serialization import SerializationService
from app.services.training.registry import RegistryService
from app.services.training.report import ReportService
from app.services.training.pipeline import TrainingPipeline


def get_experiment_repository() -> ExperimentRepository:
    return MongoExperimentRepository()


def get_training_session_repository() -> TrainingSessionRepository:
    return MongoTrainingSessionRepository()


def get_trained_model_repository() -> TrainedModelRepository:
    return MongoTrainedModelRepository()


def get_evaluation_report_repository() -> EvaluationReportRepository:
    return MongoEvaluationReportRepository()


def get_hyperparameter_set_repository() -> HyperparameterSetRepository:
    return MongoHyperparameterSetRepository()


def get_training_service() -> TrainingService:
    return TrainingService()


def get_evaluation_service() -> EvaluationService:
    return EvaluationService()


def get_comparison_service() -> ComparisonService:
    return ComparisonService()


def get_serialization_service() -> SerializationService:
    return SerializationService()


def get_report_service() -> ReportService:
    return ReportService()


def get_registry_service(
    model_repo: TrainedModelRepository = Depends(get_trained_model_repository)
) -> RegistryService:
    return RegistryService(model_repo)


def get_training_pipeline(
    dataset_repo: DatasetRepository = Depends(get_dataset_repository),
    experiment_repo: ExperimentRepository = Depends(get_experiment_repository),
    session_repo: TrainingSessionRepository = Depends(get_training_session_repository),
    model_repo: TrainedModelRepository = Depends(get_trained_model_repository),
    eval_repo: EvaluationReportRepository = Depends(get_evaluation_report_repository),
    hyper_repo: HyperparameterSetRepository = Depends(get_hyperparameter_set_repository),
    storage_service: StorageService = Depends(get_storage_service),
    training_service: TrainingService = Depends(get_training_service),
    evaluation_service: EvaluationService = Depends(get_evaluation_service),
    comparison_service: ComparisonService = Depends(get_comparison_service),
    serialization_service: SerializationService = Depends(get_serialization_service),
    report_service: ReportService = Depends(get_report_service),
) -> TrainingPipeline:
    return TrainingPipeline(
        dataset_repo=dataset_repo,
        experiment_repo=experiment_repo,
        session_repo=session_repo,
        model_repo=model_repo,
        eval_repo=eval_repo,
        hyper_repo=hyper_repo,
        storage_service=storage_service,
        training_service=training_service,
        evaluation_service=evaluation_service,
        comparison_service=comparison_service,
        serialization_service=serialization_service,
        report_service=report_service,
    )
