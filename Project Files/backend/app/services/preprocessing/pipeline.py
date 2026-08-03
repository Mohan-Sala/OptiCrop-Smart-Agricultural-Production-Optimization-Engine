import os
import time
import json
import hashlib
import uuid
import platform
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import sklearn
import joblib
from fastapi import BackgroundTasks

from app.core.config import settings
from app.core.enums import DatasetStatus, DatasetStage
from app.models.dataset import Dataset
from app.models.dataset_statistics import DatasetStatistics
from app.models.dataset_preprocessing import DatasetPreprocessing
from app.models.preprocessing_artifact import PreprocessingArtifact
from app.models.feature_metadata import FeatureMetadata

from app.repositories.interfaces.dataset import DatasetRepository
from app.repositories.interfaces.preprocessing import PreprocessingRepository
from app.repositories.interfaces.artifact import PreprocessingArtifactRepository
from app.repositories.interfaces.feature import FeatureMetadataRepository

from app.services.dataset.storage import StorageService
from app.services.preprocessing.missing_value import MissingValueService
from app.services.preprocessing.outlier import OutlierService
from app.services.preprocessing.encoding import EncodingService
from app.services.preprocessing.scaling import ScalingService
from app.services.preprocessing.validation import PreprocessingValidationService
from app.services.preprocessing.report import PreprocessingReportService

from app.utils.exceptions import ValidationException, NotFoundException, ConflictException

logger = logging.getLogger("app.services.preprocessing.pipeline")


class PreprocessingPipeline:
    """Orchestrates the end-to-end ML data preprocessing workflow, tracking lineage, artifacts, and execution checks."""

    def __init__(
        self,
        dataset_repo: DatasetRepository,
        preprocessing_repo: PreprocessingRepository,
        artifact_repo: PreprocessingArtifactRepository,
        feature_repo: FeatureMetadataRepository,
        storage_service: StorageService,
        missing_service: MissingValueService,
        outlier_service: OutlierService,
        encoding_service: EncodingService,
        scaling_service: ScalingService,
        validation_service: PreprocessingValidationService,
        report_service: PreprocessingReportService,
    ):
        self.dataset_repo = dataset_repo
        self.preprocessing_repo = preprocessing_repo
        self.artifact_repo = artifact_repo
        self.feature_repo = feature_repo
        self.storage_service = storage_service
        self.missing_service = missing_service
        self.outlier_service = outlier_service
        self.encoding_service = encoding_service
        self.scaling_service = scaling_service
        self.validation_service = validation_service
        self.report_service = report_service

    async def initiate_run(
        self,
        dataset_id: uuid.UUID,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        config: Dict[str, Any],
        background_tasks: BackgroundTasks,
    ) -> DatasetPreprocessing:
        """Saves a pending run, checks config hash for duplicate reuse, and triggers background processing."""
        # 1. Verify parent dataset exists
        parent_dataset = await self.dataset_repo.get_by_id_and_user_id(dataset_id, user_id)
        if not parent_dataset:
            raise NotFoundException("Dataset not found or access denied.")
        if parent_dataset.status != DatasetStatus.VALIDATED:
            raise ValidationException(
                f"Cannot preprocess dataset: parent dataset is in state '{parent_dataset.status}' and not fully validated."
            )

        # 2. Verify target column presence
        target_column = config.get("target_column")
        if not target_column:
            raise ValidationException("Missing target_column configuration parameter.")

        # 3. Compute unique preprocessing configuration hash
        config_str = json.dumps(config, sort_keys=True)
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()

        # 4. Try to reuse completed run with identical configurations for optimization
        existing_run = await self.preprocessing_repo.get_by_hash_and_user(config_hash, user_id)
        if existing_run:
            logger.info("Duplicate completed run found. Reusing configuration results for run %s", existing_run.id)
            return existing_run

        # 5. Populate platform and library versions for environment auditing
        env_versions = {
            "python_version": platform.python_version(),
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "sklearn_version": sklearn.__version__,
        }

        # 6. Save initial pending Preprocessing Run record
        run_id = uuid.uuid4()
        run_record = DatasetPreprocessing(
            id=run_id,
            dataset_id=dataset_id,
            user_id=user_id,
            project_id=project_id,
            status="PENDING",
            parameters=config,
            preprocessing_hash=config_hash,
            pipeline_version=parent_dataset.version,
            python_version=env_versions["python_version"],
            pandas_version=env_versions["pandas_version"],
            numpy_version=env_versions["numpy_version"],
            sklearn_version=env_versions["sklearn_version"],
            started_at=datetime.now(timezone.utc),
        )
        
        created_run = await self.preprocessing_repo.create(run_record)
        # Commit transaction immediately to release write lock and establish PENDING state
        await self.preprocessing_repo.session.commit()

        # 7. Queue background execution pipeline
        background_tasks.add_task(self.execute_pipeline, run_id, dataset_id, user_id, project_id, config)

        return created_run

    async def execute_pipeline(
        self,
        run_id: uuid.UUID,
        dataset_id: uuid.UUID,
        user_id: uuid.UUID,
        project_id: uuid.UUID,
        config: Dict[str, Any],
    ) -> None:
        """Internal background task executing data processing, joblib artifact writing, and schema persists."""
        from app.database.session import async_session
        from app.repositories.sqlalchemy.preprocessing import SqlAlchemyPreprocessingRepository
        from app.repositories.sqlalchemy.dataset import SqlAlchemyDatasetRepository
        from app.repositories.sqlalchemy.artifact import SqlAlchemyPreprocessingArtifactRepository
        from app.repositories.sqlalchemy.feature import SqlAlchemyFeatureMetadataRepository

        uploaded_supabase_paths: List[str] = []
        temp_files_to_clean: List[str] = []
        checkpoints: Dict[str, float] = {}
        lineage_map: List[Dict[str, Any]] = []

        start_time = time.time()
        target_column = config["target_column"]

        try:
            logger.info("Executing preprocessing pipeline background task for run ID: %s", run_id)

            # 1. Update run status to RUNNING
            async with async_session() as session:
                prep_repo = SqlAlchemyPreprocessingRepository(session)
                run_obj = await prep_repo.get_by_id(run_id)
                if not run_obj:
                    logger.error("Preprocessing run record %s not found.", run_id)
                    return
                run_obj.status = "RUNNING"
                await session.flush()
                await session.commit()

            # 2. Get Parent Dataset record details
            async with async_session() as session:
                dataset_repo = SqlAlchemyDatasetRepository(session)
                parent_dataset = await dataset_repo.get_by_id(dataset_id)
                if not parent_dataset:
                    raise NotFoundException("Parent dataset not found in background session.")
                parent_storage_path = parent_dataset.storage_path
                parent_version = parent_dataset.version
                parent_name = parent_dataset.name

            # --- PHASE 1: Load Dataset ---
            step_start = time.time()
            raw_bytes = await self.storage_service.download_file(parent_storage_path)
            
            os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
            temp_raw_path = os.path.join(settings.UPLOAD_PATH, f"raw_{run_id}.csv")
            with open(temp_raw_path, "wb") as f:
                f.write(raw_bytes)
            temp_files_to_clean.append(temp_raw_path)

            df = pd.read_csv(temp_raw_path, delimiter=parent_dataset.delimiter or ",", encoding=parent_dataset.encoding or "utf-8")
            df_raw_copy = df.copy()
            checkpoints["dataset_loading"] = round((time.time() - step_start) * 1000, 2)

            # --- PHASE 2: Validate Dataset Before ---
            step_start = time.time()
            self.validation_service.validate_before_preprocessing(df, target_column)
            checkpoints["validation"] = round((time.time() - step_start) * 1000, 2)

            # --- PHASE 3: Missing Value Imputation ---
            step_start = time.time()
            df, missing_summary = self.missing_service.impute(
                df, target_column, config.get("missing_value_strategies", {})
            )
            checkpoints["missing_value_processing"] = round((time.time() - step_start) * 1000, 2)

            # --- PHASE 4: Outlier Processing ---
            step_start = time.time()
            df, outlier_summary = self.outlier_service.process_outliers(
                df, target_column, config.get("outlier_strategy", {})
            )
            checkpoints["outlier_processing"] = round((time.time() - step_start) * 1000, 2)

            # --- PHASE 5: Categorical Encoding ---
            step_start = time.time()
            fitted_encoders: Dict[str, Any] = {}
            if config.get("encoding_mappings"):
                df, fitted_encoders, encode_lineage = self.encoding_service.encode(
                    df, target_column, config["encoding_mappings"]
                )
                for col_lineages in encode_lineage.values():
                    lineage_map.extend(col_lineages)
            checkpoints["encoding"] = round((time.time() - step_start) * 1000, 2)

            # --- PHASE 6: Numeric Scaling ---
            step_start = time.time()
            fitted_scalers: Dict[str, Any] = {}
            if config.get("scaling_mappings"):
                df, fitted_scalers, scale_lineage = self.scaling_service.scale(
                    df, target_column, config["scaling_mappings"]
                )
                for col_lineages in scale_lineage.values():
                    lineage_map.extend(col_lineages)
            checkpoints["scaling"] = round((time.time() - step_start) * 1000, 2)

            # --- PHASE 7: Validate Dataset After ---
            step_start = time.time()
            self.validation_service.validate_after_preprocessing(df, target_column)
            checkpoints["validation"] += round((time.time() - step_start) * 1000, 2)

            # --- PHASE 8: Generate Report ---
            step_start = time.time()
            total_time_ms = round((time.time() - start_time) * 1000, 2)
            report_data = self.report_service.compile_report(
                df_raw_copy,
                df,
                target_column,
                missing_summary,
                outlier_summary,
                lineage_map,
                checkpoints,
                total_time_ms,
            )
            checkpoints["report_generation"] = round((time.time() - step_start) * 1000, 2)
            report_data["checkpoints"] = checkpoints

            # --- PHASE 9: Joblib Transformer Serialization & Storage ---
            artifacts_to_create: List[PreprocessingArtifact] = []
            
            # Merge both encoders and scalers
            all_fitted = {**fitted_encoders, **fitted_scalers}
            for col, transformer in all_fitted.items():
                type_name = type(transformer).__name__
                temp_joblib_name = f"{run_id}_{col}_{type_name}.joblib"
                temp_joblib_path = os.path.join(settings.UPLOAD_PATH, temp_joblib_name)
                
                # Write to temp file system
                joblib.dump(transformer, temp_joblib_path)
                temp_files_to_clean.append(temp_joblib_path)
                
                # Calculate joblib checksum
                sha256 = hashlib.sha256()
                with open(temp_joblib_path, "rb") as j_f:
                    while chunk := j_f.read(8192):
                        sha256.update(chunk)
                checksum = sha256.hexdigest()
                
                # Upload joblib binary to Supabase
                storage_path = f"artifacts/{user_id}/{project_id}/{run_id}/{col}_{type_name}.joblib"
                await self.storage_service.upload_file(storage_path, temp_joblib_path, "application/octet-stream")
                uploaded_supabase_paths.append(storage_path)
                
                # Create artifact model mapping
                artifacts_to_create.append(
                    PreprocessingArtifact(
                        id=uuid.uuid4(),
                        preprocessing_run_id=run_id,
                        artifact_type=type_name,
                        storage_path=storage_path,
                        checksum=checksum,
                    )
                )

            # --- PHASE 10: Save Processed CSV Dataset & Upload ---
            temp_processed_name = f"processed_{run_id}.csv"
            temp_processed_path = os.path.join(settings.UPLOAD_PATH, temp_processed_name)
            df.to_csv(temp_processed_path, index=False)
            temp_files_to_clean.append(temp_processed_path)

            # Compute processed dataset checksum
            sha256_csv = hashlib.sha256()
            with open(temp_processed_path, "rb") as csv_f:
                while chunk := csv_f.read(8192):
                    sha256_csv.update(chunk)
            checksum_csv = sha256_csv.hexdigest()

            # Upload clean CSV file to Supabase
            new_version = parent_version + 1
            stored_filename = f"{run_id}_v{new_version}.csv"
            csv_storage_path = f"datasets/{user_id}/{project_id}/{stored_filename}"
            
            await self.storage_service.upload_file(csv_storage_path, temp_processed_path, "text/csv")
            uploaded_supabase_paths.append(csv_storage_path)

            # --- PHASE 11: Database Schema Commits (New Dataset, Stats, Features, Run details) ---
            async with async_session() as session:
                dataset_repo = SqlAlchemyDatasetRepository(session)
                artifact_repo = SqlAlchemyPreprocessingArtifactRepository(session)
                feature_repo = SqlAlchemyFeatureMetadataRepository(session)
                prep_repo = SqlAlchemyPreprocessingRepository(session)

                # 1. Create derived dataset version record
                new_dataset_id = uuid.uuid4()
                new_dataset = Dataset(
                    id=new_dataset_id,
                    project_id=project_id,
                    user_id=user_id,
                    name=f"{parent_name}_preprocessed",
                    original_filename=f"{parent_name}_preprocessed.csv",
                    stored_filename=stored_filename,
                    storage_path=csv_storage_path,
                    version=new_version,
                    parent_dataset_id=dataset_id,
                    is_latest=True,
                    dataset_stage=DatasetStage.PREPROCESSED,
                    status=DatasetStatus.VALIDATED,
                    rows=df.shape[0],
                    columns=df.shape[1],
                    size=os.path.getsize(temp_processed_path),
                    delimiter=",",
                    encoding="utf-8",
                    sha256_checksum=checksum_csv,
                    description=f"Preprocessed version of dataset {parent_name}",
                )

                # Trigger trigger latest version toggle mapping
                parent_dataset_obj = await dataset_repo.get_by_id(dataset_id)
                if parent_dataset_obj:
                    parent_dataset_obj.is_latest = False

                created_dataset = await dataset_repo.create(new_dataset)
                await session.flush()

                # 2. Persist dataset statistics
                # Calculate summary profile stats
                stats_profile = report_data["duplicate_summary"]
                stats_record = DatasetStatistics(
                    dataset_id=new_dataset_id,
                    missing_values=report_data["missing_value_summary"],
                    duplicate_rows=stats_profile["processed_duplicate_rows"],
                    duplicate_columns=0,
                    memory_usage=int(df.memory_usage(deep=True).sum()),
                    column_summary=report_data["baseline_profile"],
                )
                session.add(stats_record)

                # 3. Create feature metadata catalog batch mappings
                features_catalog: List[FeatureMetadata] = []
                for item in report_data["feature_summary"]:
                    features_catalog.append(
                        FeatureMetadata(
                            id=uuid.uuid4(),
                            dataset_id=new_dataset_id,
                            feature_name=item["feature_name"],
                            feature_type=item["feature_type"],
                            nullable=item["nullable"],
                            encoded=item["encoded"],
                            scaled=item["scaled"],
                            generated=item["generated"],
                            target=item["target"],
                        )
                    )
                await feature_repo.create_features_batch(features_catalog)

                # 4. Save artifacts
                for art in artifacts_to_create:
                    art.preprocessing_run_id = run_id
                    session.add(art)

                # 5. Finalize execution run details
                run_obj = await prep_repo.get_by_id(run_id)
                if run_obj:
                    run_obj.status = "COMPLETED"
                    run_obj.preprocessed_dataset_id = new_dataset_id
                    run_obj.report = report_data
                    run_obj.completed_at = datetime.now(timezone.utc)

                await session.flush()
                await session.commit()

            logger.info("Successfully completed Preprocessing Run: %s", run_id)

        except Exception as e:
            logger.error("Preprocessing run failed for run ID: %s. Error: %s", run_id, str(e), exc_info=True)
            
            # --- CRITICAL ROLLBACK: Supabase File purges & Database Recovery ---
            for path in uploaded_supabase_paths:
                try:
                    await self.storage_service.delete_file(path)
                except Exception as del_err:
                    logger.warning("Supabase rollback cleanup failed for path %s: %s", path, str(del_err))

            async with async_session() as session:
                prep_repo = SqlAlchemyPreprocessingRepository(session)
                run_obj = await prep_repo.get_by_id(run_id)
                if run_obj:
                    run_obj.status = "FAILED"
                    run_obj.error_message = str(e)
                    run_obj.completed_at = datetime.now(timezone.utc)
                    await session.flush()
                    await session.commit()
        finally:
            # Clean up all temporary files generated on local disk
            for file_path in temp_files_to_clean:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as cleanup_err:
                        logger.warning("Cleanup failed for temp path %s: %s", file_path, str(cleanup_err))
