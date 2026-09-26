from fastapi import Depends

from app.repositories.interfaces.prediction import PredictionRepository
from app.repositories.interfaces.prediction_history import PredictionHistoryRepository
from app.repositories.interfaces.prediction_audit import PredictionAuditRepository
from app.repositories.interfaces.trained_model import TrainedModelRepository
from app.repositories.interfaces.dataset import DatasetRepository

from app.repositories.mongodb.prediction import MongoPredictionRepository
from app.repositories.mongodb.prediction_history import MongoPredictionHistoryRepository
from app.repositories.mongodb.prediction_audit import MongoPredictionAuditRepository
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


def get_prediction_repository() -> PredictionRepository:
    return MongoPredictionRepository()


def get_prediction_history_repository() -> PredictionHistoryRepository:
    return MongoPredictionHistoryRepository()


def get_prediction_audit_repository() -> PredictionAuditRepository:
    return MongoPredictionAuditRepository()


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
    effective_repo = repo if type(repo).__name__ != "Depends" else get_prediction_history_repository()
    return PredictionHistoryService(effective_repo)


def get_prediction_serialization_service(
    storage_service: StorageService = Depends(get_storage_service)
) -> PredictionSerializationService:
    effective_storage = storage_service if type(storage_service).__name__ != "Depends" else get_storage_service()
    return PredictionSerializationService(effective_storage)


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
        prediction_repo=prediction_repo if type(prediction_repo).__name__ != "Depends" else get_prediction_repository(),
        trained_model_repo=trained_model_repo if type(trained_model_repo).__name__ != "Depends" else get_trained_model_repository(),
        dataset_repo=dataset_repo if type(dataset_repo).__name__ != "Depends" else get_dataset_repository(),
        validation_service=validation_service if type(validation_service).__name__ != "Depends" else get_prediction_validation_service(),
        preprocessing_service=preprocessing_service if type(preprocessing_service).__name__ != "Depends" else get_prediction_preprocessing_service(),
        inference_service=inference_service if type(inference_service).__name__ != "Depends" else get_inference_service(),
        serialization_service=serialization_service if type(serialization_service).__name__ != "Depends" else get_prediction_serialization_service(),
        prediction_cache=prediction_cache if type(prediction_cache).__name__ != "Depends" else get_prediction_cache(),
        warm_model_cache=warm_model_cache if type(warm_model_cache).__name__ != "Depends" else get_warm_model_cache(),
    )
