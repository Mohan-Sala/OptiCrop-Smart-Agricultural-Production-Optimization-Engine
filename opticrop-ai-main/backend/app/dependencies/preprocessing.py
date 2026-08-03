from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.interfaces.dataset import DatasetRepository
from app.repositories.interfaces.preprocessing import PreprocessingRepository
from app.repositories.interfaces.artifact import PreprocessingArtifactRepository
from app.repositories.interfaces.feature import FeatureMetadataRepository

from app.repositories.sqlalchemy.dataset import SqlAlchemyDatasetRepository
from app.repositories.sqlalchemy.preprocessing import SqlAlchemyPreprocessingRepository
from app.repositories.sqlalchemy.artifact import SqlAlchemyPreprocessingArtifactRepository
from app.repositories.sqlalchemy.feature import SqlAlchemyFeatureMetadataRepository

from app.services.dataset.storage import StorageService
from app.dependencies.dataset import get_dataset_repository, get_storage_service

from app.services.preprocessing.missing_value import MissingValueService
from app.services.preprocessing.outlier import OutlierService
from app.services.preprocessing.encoding import EncodingService
from app.services.preprocessing.scaling import ScalingService
from app.services.preprocessing.validation import PreprocessingValidationService
from app.services.preprocessing.report import PreprocessingReportService
from app.services.preprocessing.pipeline import PreprocessingPipeline


def get_preprocessing_repository(db: AsyncSession = Depends(get_db)) -> PreprocessingRepository:
    return SqlAlchemyPreprocessingRepository(db)


def get_artifact_repository(db: AsyncSession = Depends(get_db)) -> PreprocessingArtifactRepository:
    return SqlAlchemyPreprocessingArtifactRepository(db)


def get_feature_repository(db: AsyncSession = Depends(get_db)) -> FeatureMetadataRepository:
    return SqlAlchemyFeatureMetadataRepository(db)


def get_missing_service() -> MissingValueService:
    return MissingValueService()


def get_outlier_service() -> OutlierService:
    return OutlierService()


def get_encoding_service() -> EncodingService:
    return EncodingService()


def get_scaling_service() -> ScalingService:
    return ScalingService()


def get_preprocessing_validation_service() -> PreprocessingValidationService:
    return PreprocessingValidationService()


def get_report_service() -> PreprocessingReportService:
    return PreprocessingReportService()


def get_preprocessing_pipeline(
    dataset_repo: DatasetRepository = Depends(get_dataset_repository),
    preprocessing_repo: PreprocessingRepository = Depends(get_preprocessing_repository),
    artifact_repo: PreprocessingArtifactRepository = Depends(get_artifact_repository),
    feature_repo: FeatureMetadataRepository = Depends(get_feature_repository),
    storage_service: StorageService = Depends(get_storage_service),
    missing_service: MissingValueService = Depends(get_missing_service),
    outlier_service: OutlierService = Depends(get_outlier_service),
    encoding_service: EncodingService = Depends(get_encoding_service),
    scaling_service: ScalingService = Depends(get_scaling_service),
    validation_service: PreprocessingValidationService = Depends(get_preprocessing_validation_service),
    report_service: PreprocessingReportService = Depends(get_report_service),
) -> PreprocessingPipeline:
    return PreprocessingPipeline(
        dataset_repo=dataset_repo,
        preprocessing_repo=preprocessing_repo,
        artifact_repo=artifact_repo,
        feature_repo=feature_repo,
        storage_service=storage_service,
        missing_service=missing_service,
        outlier_service=outlier_service,
        encoding_service=encoding_service,
        scaling_service=scaling_service,
        validation_service=validation_service,
        report_service=report_service,
    )
