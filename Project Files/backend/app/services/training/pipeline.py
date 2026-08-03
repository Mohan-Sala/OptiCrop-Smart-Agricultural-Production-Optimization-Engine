import os
import time
import json
import hashlib
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from fastapi import BackgroundTasks
from sqlalchemy import select, update

from app.core.config import settings
from app.core.enums import DatasetStatus, DatasetStage
from app.models.dataset import Dataset
from app.models.training_experiment import TrainingExperiment
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.models.model_metric import ModelMetric
from app.models.evaluation_report import EvaluationReport
from app.models.hyperparameter_set import HyperparameterSet
from app.models.dataset_preprocessing import DatasetPreprocessing

from app.repositories.interfaces.dataset import DatasetRepository
from app.repositories.interfaces.experiment import ExperimentRepository
from app.repositories.interfaces.training_session import TrainingSessionRepository
from app.repositories.interfaces.trained_model import TrainedModelRepository
from app.repositories.interfaces.evaluation import EvaluationReportRepository
from app.repositories.interfaces.hyperparameter import HyperparameterSetRepository

from app.services.dataset.storage import StorageService
from app.services.training.training import TrainingService
from app.services.training.evaluation import EvaluationService
from app.services.training.comparison import ComparisonService
from app.services.training.serialization import SerializationService
from app.services.training.report import ReportService
from app.utils.exceptions import ValidationException, NotFoundException

logger = logging.getLogger("app.services.training.pipeline")


class TrainingPipeline:
    """Orchestrates end-to-end ML model training sessions, validating signatures, splits, locking datasets, and serializing winning estimators."""

    def __init__(
        self,
        dataset_repo: DatasetRepository,
        experiment_repo: ExperimentRepository,
        session_repo: TrainingSessionRepository,
        model_repo: TrainedModelRepository,
        eval_repo: EvaluationReportRepository,
        hyper_repo: HyperparameterSetRepository,
        storage_service: StorageService,
        training_service: TrainingService,
        evaluation_service: EvaluationService,
        comparison_service: ComparisonService,
        serialization_service: SerializationService,
        report_service: ReportService,
    ):
        self.dataset_repo = dataset_repo
        self.experiment_repo = experiment_repo
        self.session_repo = session_repo
        self.model_repo = model_repo
        self.eval_repo = eval_repo
        self.hyper_repo = hyper_repo
        self.storage_service = storage_service
        self.training_service = training_service
        self.evaluation_service = evaluation_service
        self.comparison_service = comparison_service
        self.serialization_service = serialization_service
        self.report_service = report_service

    async def initiate_run(
        self,
        dataset_id: uuid.UUID,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        config: Dict[str, Any],
        background_tasks: BackgroundTasks,
    ) -> TrainingSession:
        # 1. Verify experiment ownership
        exp_id = uuid.UUID(str(config["experiment_id"]))
        experiment = await self.experiment_repo.get_by_id(exp_id)
        if not experiment or experiment.project_id != project_id:
            raise NotFoundException("Experiment not found or access denied.")

        # 2. Verify dataset stage matches PREPROCESSED
        dataset = await self.dataset_repo.get_by_id_and_user_id(dataset_id, user_id)
        if not dataset:
            raise NotFoundException("Dataset not found or access denied.")
        if dataset.dataset_stage != DatasetStage.PREPROCESSED or dataset.status != DatasetStatus.VALIDATED:
            raise ValidationException("Only validated preprocessed datasets can be used for model training.")

        # 3. Retrieve preprocessing hash for training configuration hash
        # We query the database context directly using the repo session
        stmt = select(DatasetPreprocessing).where(
            DatasetPreprocessing.preprocessed_dataset_id == dataset_id,
            DatasetPreprocessing.status == "COMPLETED"
        ).order_by(DatasetPreprocessing.created_at.desc())
        prep_run = (await self.session_repo.session.execute(stmt)).scalars().first()
        prep_hash = prep_run.preprocessing_hash if prep_run else "no_prep"

        # 4. Generate deterministic training configuration hash
        algorithms_sorted = sorted(config.get("algorithms", []))
        hyperparams_sorted = json.dumps(config.get("hyperparameters", {}), sort_keys=True)
        cv_strategy_sorted = json.dumps(config.get("cv_strategy", {}), sort_keys=True)
        seed = config.get("training_seed", 42)
        test_size = config.get("test_size", 0.2)
        shuffle = config.get("shuffle", True)

        hash_payload = f"{dataset.version}:{prep_hash}:{algorithms_sorted}:{hyperparams_sorted}:{cv_strategy_sorted}:{seed}:{test_size}:{shuffle}"
        config_hash = hashlib.sha256(hash_payload.encode()).hexdigest()

        # 5. Reuse completed training config run
        existing_run = await self.session_repo.get_by_hash_and_user(config_hash, user_id)
        if existing_run:
            logger.info("Duplicate training configuration run found. Reusing training session %s", existing_run.id)
            return existing_run

        # Ensure config has no raw UUID objects so it is JSON serializable
        serializable_config = {}
        for k, v in config.items():
            if isinstance(v, uuid.UUID):
                serializable_config[k] = str(v)
            elif isinstance(v, (dict, list)):
                serializable_config[k] = json.loads(json.dumps(v, default=str))
            else:
                serializable_config[k] = v

        # 6. Save initial pending TrainingSession record
        run_id = uuid.uuid4()
        session_record = TrainingSession(
            id=run_id,
            dataset_id=dataset_id,
            experiment_id=exp_id,
            preprocessing_run_id=prep_run.id if prep_run else None,
            user_id=user_id,
            problem_type=config["problem_type"],
            target_column=dataset.feature_catalog[0].feature_name if dataset.feature_catalog else "target", # Default fallback
            status="PENDING",
            config=serializable_config,
            training_seed=seed,
            test_size=test_size,
            shuffle=shuffle,
            stratify_column=config.get("stratify_column"),
            cv_seed=seed,
            config_hash=config_hash,
            started_at=datetime.now(timezone.utc),
        )
        
        # Pull correct target column name from database Feature Metadata catalog
        for feat in dataset.feature_catalog:
            if feat.target:
                session_record.target_column = feat.feature_name
                break

        created_session = await self.session_repo.create(session_record)
        await self.session_repo.session.commit()

        # 7. Queue background execution
        background_tasks.add_task(self.execute_pipeline, run_id, dataset_id, user_id, project_id, config)

        return created_session

    async def execute_pipeline(
        self,
        run_id: uuid.UUID,
        dataset_id: uuid.UUID,
        user_id: uuid.UUID,
        project_id: uuid.UUID,
        config: Dict[str, Any],
    ) -> None:
        from app.database.session import async_session
        from app.repositories.sqlalchemy.training_session import SqlAlchemyTrainingSessionRepository
        from app.repositories.sqlalchemy.trained_model import SqlAlchemyTrainedModelRepository
        from app.repositories.sqlalchemy.dataset import SqlAlchemyDatasetRepository
        from app.repositories.sqlalchemy.feature import SqlAlchemyFeatureMetadataRepository

        temp_files_to_clean: List[str] = []
        uploaded_supabase_paths: List[str] = []
        start_time = time.time()

        try:
            logger.info("Executing training pipeline background job for session: %s", run_id)

            # 1. Update session status to TRAINING and lock dataset
            async with async_session() as session:
                sess_repo = SqlAlchemyTrainingSessionRepository(session)
                ds_repo = SqlAlchemyDatasetRepository(session)
                
                run_obj = await sess_repo.get_by_id(run_id)
                if run_obj:
                    run_obj.status = "TRAINING"
                
                dataset_obj = await ds_repo.get_by_id(dataset_id)
                if dataset_obj:
                    dataset_obj.locked_by_training = True
                
                await session.flush()
                await session.commit()

            # 2. Fetch raw parameters and configuration details
            async with async_session() as session:
                ds_repo = SqlAlchemyDatasetRepository(session)
                feat_repo = SqlAlchemyFeatureMetadataRepository(session)
                
                dataset_obj = await ds_repo.get_by_id(dataset_id)
                if not dataset_obj:
                    raise NotFoundException("Dataset not found in training session.")
                storage_path = dataset_obj.storage_path
                delimiter = dataset_obj.delimiter or ","
                encoding = dataset_obj.encoding or "utf-8"
                dataset_version = dataset_obj.version
                dataset_checksum = dataset_obj.sha256_checksum

                features = await feat_repo.get_by_dataset_id(dataset_id)
                if not features:
                    raise ValidationException("Feature catalog is missing for target preprocessed dataset.")

            # 3. Load dataset CSV in memory
            csv_bytes = await self.storage_service.download_file(storage_path)
            os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
            temp_csv_path = os.path.join(settings.UPLOAD_PATH, f"train_{run_id}.csv")
            with open(temp_csv_path, "wb") as f:
                f.write(csv_bytes)
            temp_files_to_clean.append(temp_csv_path)

            df = pd.read_csv(temp_csv_path, delimiter=delimiter, encoding=encoding)

            # 4. Resolve Target Column and Features
            target_column = None
            for f in features:
                if f.target:
                    target_column = f.feature_name
                    break
            if not target_column or target_column not in df.columns:
                raise ValidationException(f"Target column '{target_column}' is missing from loaded dataframe.")

            # Filter inputs mapping: Exclude target and generated outlier flags
            feature_names = [
                f.feature_name for f in features 
                if not f.target and not f.generated and f.feature_name in df.columns
            ]
            if not feature_names:
                raise ValidationException("At least 1 valid feature column must be mapped.")

            X = df[feature_names]
            y = df[target_column]

            # --- EARLY VALIDATION CHECKS ---
            if X.shape[0] < 10:
                raise ValidationException(f"Sample size of {X.shape[0]} is too small. Minimum required is 10.")
            if X.shape[1] < 1:
                raise ValidationException("Zero features remaining for model fitting.")
            
            problem_type = config["problem_type"]
            if problem_type == "classification":
                unique_classes = y.nunique()
                if unique_classes < 2:
                    raise ValidationException(
                        f"Classification target '{target_column}' must contain at least 2 distinct classes. Found: {unique_classes}."
                    )
            elif problem_type == "regression":
                y_std = y.std()
                if pd.isnull(y_std) or y_std == 0:
                    raise ValidationException(f"Regression target '{target_column}' has zero variance (std = 0).")
            else:
                raise ValidationException(f"Unknown problem type: {problem_type}")

            # 5. Split Dataset into Train/Test partitions
            seed = config.get("training_seed", 42)
            test_size = config.get("test_size", 0.2)
            shuffle = config.get("shuffle", True)

            # Split logic preserving indices
            np.random.seed(seed)
            if shuffle:
                shuffled_indices = np.random.permutation(len(df))
            else:
                shuffled_indices = np.arange(len(df))

            test_set_size = int(len(df) * test_size)
            test_indices = shuffled_indices[:test_set_size]
            train_indices = shuffled_indices[test_set_size:]

            X_train, X_test = X.iloc[train_indices], X.iloc[test_indices]
            y_train, y_test = y.iloc[train_indices], y.iloc[test_indices]

            # 6. Fit Estimators and track Experiment history
            trained_results: Dict[str, Dict[str, Any]] = {}
            algorithms = config.get("algorithms", [])
            hyperparameters_grid = config.get("hyperparameters", {})
            cv_strategy = config.get("cv_strategy", {"method": "KFold", "folds": 5})

            for algo in algorithms:
                algo_start = time.time()
                param_grid = hyperparameters_grid.get(algo, {})
                
                # Train and cross-validate algorithm
                model_obj, best_params, fold_scores = self.training_service.train_algorithm(
                    X_train, y_train, algo, problem_type, param_grid, cv_strategy, seed
                )
                
                # Evaluate model on test fold partition
                val_metrics, visual_metrics = self.evaluation_service.evaluate_model(
                    model_obj, X_test, y_test, problem_type
                )
                
                trained_results[algo] = {
                    "model_object": model_obj,
                    "hyperparameters": best_params,
                    "metrics": val_metrics,
                    "visuals": visual_metrics,
                    "cv_scores": fold_scores,
                    "training_time": round((time.time() - algo_start) * 1000, 2),
                }

            # 7. Automatically compare and identify the winner model
            winner_algo, comparison_table, select_reason = self.comparison_service.select_best_model(
                trained_results, problem_type
            )
            
            winner_data = trained_results[winner_algo]
            winner_model = winner_data["model_object"]

            # 8. Serialize winning model to joblib and get checksum
            model_uuid = uuid.uuid4()
            temp_joblib_path, model_checksum = self.serialization_service.serialize_model(winner_model, model_uuid)
            temp_files_to_clean.append(temp_joblib_path)

            # 9. Upload model joblib file to Supabase storage
            exp_id = config["experiment_id"]
            model_version = f"1.0.{int(time.time())}" # Deterministic increment version schema
            storage_model_path = f"models/{user_id}/{project_id}/{exp_id}/{model_version}.joblib"
            
            await self.storage_service.upload_file(storage_model_path, temp_joblib_path, "application/octet-stream")
            uploaded_supabase_paths.append(storage_model_path)

            # 10. Pull parent preprocessing details to map model signature
            async with async_session() as session:
                stmt_prep = select(DatasetPreprocessing).where(
                    DatasetPreprocessing.preprocessed_dataset_id == dataset_id,
                    DatasetPreprocessing.status == "COMPLETED"
                ).order_by(DatasetPreprocessing.created_at.desc())
                prep_run = (await session.execute(stmt_prep)).scalars().first()
                prep_run_id = prep_run.id if prep_run else None

            # Compile expected model signature
            signature = {
                "feature_names": feature_names,
                "feature_count": len(feature_names),
                "target_column": target_column,
                "expected_dtypes": {col: str(X[col].dtype) for col in feature_names},
                "preprocessing_artifact_version": dataset_version,
                "preprocessing_run_id": str(prep_run_id) if prep_run_id else None,
                "dataset_version": dataset_version,
                "training_dataset_checksum": dataset_checksum,
            }

            # 11. Write Registry tables
            async with async_session() as session:
                sess_repo = SqlAlchemyTrainingSessionRepository(session)
                model_repo = SqlAlchemyTrainedModelRepository(session)

                # Save TrainedModel registry entry
                trained_model_record = TrainedModel(
                    id=model_uuid,
                    training_session_id=run_id,
                    model_name=f"{winner_algo}_model",
                    algorithm=winner_algo,
                    storage_path=storage_model_path,
                    version=model_version,
                    is_active=False, # Wait for explicit activation
                    status="READY",
                    checksum=model_checksum,
                    hyperparameters=winner_data["hyperparameters"],
                    signature=signature,
                )
                session.add(trained_model_record)
                await session.flush()

                # Save evaluation report visuals
                eval_report_record = EvaluationReport(
                    id=uuid.uuid4(),
                    trained_model_id=model_uuid,
                    report_data={
                        "comparison_table": comparison_table,
                        "selection_reason": select_reason,
                        "winner_metrics": winner_data["metrics"],
                        "winner_visuals": winner_data["visuals"],
                        "cv_scores": winner_data["cv_scores"],
                    }
                )
                session.add(eval_report_record)

                # Save hyperparameter set
                hyper_set_record = HyperparameterSet(
                    id=uuid.uuid4(),
                    trained_model_id=model_uuid,
                    parameters=winner_data["hyperparameters"],
                )
                session.add(hyper_set_record)

                # Save flat metrics summary
                for metric_name, val in winner_data["metrics"].items():
                    metric_record = ModelMetric(
                        id=uuid.uuid4(),
                        trained_model_id=model_uuid,
                        metric_name=metric_name,
                        metric_value=val,
                    )
                    session.add(metric_record)

                # Finalize TrainingSession status
                run_obj = await sess_repo.get_by_id(run_id)
                if run_obj:
                    run_obj.status = "COMPLETED"
                    run_obj.best_model = f"{winner_algo}_model"
                    run_obj.training_time = round(time.time() - start_time, 2)
                    run_obj.storage_model_path = storage_model_path
                    run_obj.completed_at = datetime.now(timezone.utc)

                await session.flush()
                await session.commit()

            logger.info("Successfully completed Training Session: %s. Winner: %s", run_id, winner_algo)

        except Exception as e:
            logger.error("Training session failed for run ID: %s. Error: %s", run_id, str(e), exc_info=True)
            
            # --- CRITICAL ROLLBACK: Supabase File purges & Database Recovery ---
            for path in uploaded_supabase_paths:
                try:
                    await self.storage_service.delete_file(path)
                except Exception as del_err:
                    logger.warning("Supabase rollback cleanup failed for path %s: %s", path, str(del_err))

            async with async_session() as session:
                sess_repo = SqlAlchemyTrainingSessionRepository(session)
                run_obj = await sess_repo.get_by_id(run_id)
                if run_obj:
                    run_obj.status = "FAILED"
                    # We modify best_model to store error stack traces, and complete timestamp
                    run_obj.completed_at = datetime.now(timezone.utc)
                    # We store error inside a custom db attribute or log it
                await session.flush()
                await session.commit()
        finally:
            # --- CRITICAL UNLOCK DATASET ---
            try:
                async with async_session() as session:
                    ds_repo = SqlAlchemyDatasetRepository(session)
                    dataset_obj = await ds_repo.get_by_id(dataset_id)
                    if dataset_obj:
                        dataset_obj.locked_by_training = False
                    await session.flush()
                    await session.commit()
            except Exception as unlock_err:
                logger.error("Failed to unlock dataset %s: %s", dataset_id, str(unlock_err))

            # Clean local files
            for file_path in temp_files_to_clean:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as cleanup_err:
                        logger.warning("Cleanup failed for temp path %s: %s", file_path, str(cleanup_err))
