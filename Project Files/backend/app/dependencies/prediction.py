from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.interfaces.prediction import PredictionRepository
from app.repositories.interfaces.prediction_history import PredictionHistoryRepository
from app.repositories.interfaces.prediction_audit import PredictionAuditRepository
from app.repositories.interfaces.trained_model import TrainedModelRepository
from app.repositories.interfaces.dataset import DatasetRepository

from app.repositories.sqlalchemy.prediction import SqlAlchemyPredictionRepository
from app.repositories.sqlalchemy.prediction_history import SqlAlchemyPredictionHistoryRepository
from app.repositories.sqlalchemy.prediction_audit import SqlAlchemyPredictionAuditRepository
from app.dependencies.training import get_trained_model_repository
from app.dependencies.dataset import get_dataset_repository, get_storage_service
from app.services.dataset.storage import StorageService

from app.services.prediction.cache import PredictionCache, WarmModelCache
from app.services.prediction.validation import PredictionValidationService
from app.services.prediction.preprocessing import PredictionPreprocessingService
from app.services.prediction.inference import InferenceService
from app.services.prediction.export import PredictionExportService
from app.services.prediction.history import PredictionHistoryService
from app.services.prediction.serialization import PredictionSerializationService
from app.services.prediction.pipeline import PredictionPipeline

# Singletons caching contexts
_prediction_cache_instance = PredictionCache()
_warm_model_cache_instance = WarmModelCache()


def get_prediction_repository(db: AsyncSession = Depends(get_db)) -> PredictionRepository:
    return SqlAlchemyPredictionRepository(db)


def get_prediction_history_repository(db: AsyncSession = Depends(get_db)) -> PredictionHistoryRepository:
    return SqlAlchemyPredictionHistoryRepository(db)


def get_prediction_audit_repository(db: AsyncSession = Depends(get_db)) -> PredictionAuditRepository:
    return SqlAlchemyPredictionAuditRepository(db)


def get_prediction_cache() -> PredictionCache:
    return _prediction_cache_instance


def get_warm_model_cache() -> WarmModelCache:
    return _warm_model_cache_instance


def get_prediction_validation_service() -> PredictionValidationService:
    return PredictionValidationService()


def get_prediction_preprocessing_service() -> PredictionPreprocessingService:
    return PredictionPreprocessingService()


def get_inference_service() -> InferenceService:
    return InferenceService()


def get_prediction_export_service() -> PredictionExportService:
    return PredictionExportService()


def get_prediction_history_service(
    repo: PredictionHistoryRepository = Depends(get_prediction_history_repository)
) -> PredictionHistoryService:
    return PredictionHistoryService(repo)


def get_prediction_serialization_service(
    storage_service: StorageService = Depends(get_storage_service)
) -> PredictionSerializationService:
    return PredictionSerializationService(storage_service)


def get_prediction_pipeline(
    prediction_repo: PredictionRepository = Depends(get_prediction_repository),
    trained_model_repo: TrainedModelRepository = Depends(get_trained_model_repository),
    dataset_repo: DatasetRepository = Depends(get_dataset_repository),
    validation_service: PredictionValidationService = Depends(get_prediction_validation_service),
    preprocessing_service: PredictionPreprocessingService = Depends(get_prediction_preprocessing_service),
    inference_service: InferenceService = Depends(get_inference_service),
    serialization_service: PredictionSerializationService = Depends(get_prediction_serialization_service),
    prediction_cache: PredictionCache = Depends(get_prediction_cache),
    warm_model_cache: WarmModelCache = Depends(get_warm_model_cache),
) -> PredictionPipeline:
    return PredictionPipeline(
        prediction_repo=prediction_repo,
        trained_model_repo=trained_model_repo,
        dataset_repo=dataset_repo,
        validation_service=validation_service,
        preprocessing_service=preprocessing_service,
        inference_service=inference_service,
        serialization_service=serialization_service,
        prediction_cache=prediction_cache,
        warm_model_cache=warm_model_cache,
    )
