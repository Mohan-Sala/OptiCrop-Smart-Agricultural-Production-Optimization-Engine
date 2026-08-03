from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.interfaces.dataset import DatasetRepository
from app.repositories.interfaces.experiment import ExperimentRepository
from app.repositories.interfaces.training_session import TrainingSessionRepository
from app.repositories.interfaces.trained_model import TrainedModelRepository
from app.repositories.interfaces.evaluation import EvaluationReportRepository
from app.repositories.interfaces.hyperparameter import HyperparameterSetRepository

from app.repositories.sqlalchemy.dataset import SqlAlchemyDatasetRepository
from app.repositories.sqlalchemy.experiment import SqlAlchemyExperimentRepository
from app.repositories.sqlalchemy.training_session import SqlAlchemyTrainingSessionRepository
from app.repositories.sqlalchemy.trained_model import SqlAlchemyTrainedModelRepository
from app.repositories.sqlalchemy.evaluation import SqlAlchemyEvaluationReportRepository
from app.repositories.sqlalchemy.hyperparameter import SqlAlchemyHyperparameterSetRepository

from app.services.dataset.storage import StorageService
from app.dependencies.dataset import get_dataset_repository, get_storage_service

from app.services.training.training import TrainingService
from app.services.training.evaluation import EvaluationService
from app.services.training.comparison import ComparisonService
from app.services.training.serialization import SerializationService
from app.services.training.registry import RegistryService
from app.services.training.report import ReportService
from app.services.training.pipeline import TrainingPipeline


def get_experiment_repository(db: AsyncSession = Depends(get_db)) -> ExperimentRepository:
    return SqlAlchemyExperimentRepository(db)


def get_training_session_repository(db: AsyncSession = Depends(get_db)) -> TrainingSessionRepository:
    return SqlAlchemyTrainingSessionRepository(db)


def get_trained_model_repository(db: AsyncSession = Depends(get_db)) -> TrainedModelRepository:
    return SqlAlchemyTrainedModelRepository(db)


def get_evaluation_report_repository(db: AsyncSession = Depends(get_db)) -> EvaluationReportRepository:
    return SqlAlchemyEvaluationReportRepository(db)


def get_hyperparameter_set_repository(db: AsyncSession = Depends(get_db)) -> HyperparameterSetRepository:
    return SqlAlchemyHyperparameterSetRepository(db)


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
