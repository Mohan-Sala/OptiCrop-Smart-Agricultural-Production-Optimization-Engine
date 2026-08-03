import time
import uuid
import asyncio
import logging
import hashlib
from datetime import datetime, timezone
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

from app.models.prediction_run import PredictionRun, PredictionStatus
from app.models.trained_model import TrainedModel
from app.repositories.interfaces.prediction import PredictionRepository
from app.repositories.interfaces.trained_model import TrainedModelRepository
from app.repositories.interfaces.dataset import DatasetRepository
from app.services.prediction.cache import PredictionCache, WarmModelCache
from app.services.prediction.validation import PredictionValidationService
from app.services.prediction.preprocessing import PredictionPreprocessingService
from app.services.prediction.inference import InferenceService
from app.services.prediction.serialization import PredictionSerializationService
from app.utils.exceptions import NotFoundException, ValidationException

logger = logging.getLogger("app.services.prediction.pipeline")


class PredictionPipelineContext:
    def __init__(
        self,
        user_id: uuid.UUID,
        project_id: uuid.UUID,
        model_id: Optional[uuid.UUID] = None,
        idempotency_key: Optional[str] = None,
        include_explanation: bool = False,
    ):
        self.user_id = user_id
        self.project_id = project_id
        self.model_id = model_id
        self.idempotency_key = idempotency_key
        self.include_explanation = include_explanation
        self.generated_at = datetime.now(timezone.utc)
        
        # Pipeline State
        self.active_model: Optional[TrainedModel] = None
        self.dataset_id: Optional[uuid.UUID] = None
        self.preprocessing_run_id: Optional[uuid.UUID] = None
        self.model_version: int = 1
        self.model_checksum: str = ""
        self.model_signature_checksum: str = ""
        self.dataset_version: int = 1
        self.request_hash: str = ""
        
        # Timing audits (Phase 9 monitoring readiness)
        self.timing_validation: float = 0.0
        self.timing_preprocessing: float = 0.0
        self.timing_loading: float = 0.0
        self.timing_prediction: float = 0.0
        self.timing_serialization: float = 0.0


class PredictionPipeline:
    """Orchestrates end-to-end real-time and batch predictions execution pipelines."""

    def __init__(
        self,
        prediction_repo: PredictionRepository,
        trained_model_repo: TrainedModelRepository,
        dataset_repo: DatasetRepository,
        validation_service: PredictionValidationService,
        preprocessing_service: PredictionPreprocessingService,
        inference_service: InferenceService,
        serialization_service: PredictionSerializationService,
        prediction_cache: PredictionCache,
        warm_model_cache: WarmModelCache,
    ):
        self.prediction_repo = prediction_repo
        self.trained_model_repo = trained_model_repo
        self.dataset_repo = dataset_repo
        self.validation_service = validation_service
        self.preprocessing_service = preprocessing_service
        self.inference_service = inference_service
        self.serialization_service = serialization_service
        self.prediction_cache = prediction_cache
        self.warm_model_cache = warm_model_cache

    async def execute_run(
        self,
        ctx: PredictionPipelineContext,
        features_list: List[Dict[str, Any]],
        timeout_seconds: float = 30.0,
    ) -> PredictionRun:
        """Executes inputs validation, transforms imputation/scaling, runs estimator predictions."""
        start_total = time.time()
        
        # 1. Prediction run audit setup
        run_id = uuid.uuid4()
        prediction_run = PredictionRun(
            id=run_id,
            user_id=ctx.user_id,
            project_id=ctx.project_id,
            model_id=uuid.UUID("00000000-0000-0000-0000-000000000000"), # Placeholder updated later
            model_version=1,
            model_checksum="temp",
            model_signature_checksum="temp",
            dataset_version=1,
            preprocessing_run_id=None,
            prediction_count=len(features_list),
            request_hash="temp",
            idempotency_key=ctx.idempotency_key,
            status=PredictionStatus.PENDING,
            request_payload={"features": features_list},
        )
        
        # Save pending record to enable batch monitoring status checks
        await self.prediction_repo.create(prediction_run)
        await self.prediction_repo.session.flush()
        await self.prediction_repo.session.commit()

        try:
            # Wrap core pipeline execution in timeout policy guard
            await asyncio.wait_for(
                self._execute_pipeline_steps(ctx, prediction_run, features_list),
                timeout=timeout_seconds
            )
            prediction_run.status = PredictionStatus.COMPLETED
            prediction_run.execution_time = round(time.time() - start_total, 4)
            
            # Commit success
            await self.prediction_repo.session.commit()
            return prediction_run
            
        except asyncio.TimeoutError as te:
            prediction_run.status = PredictionStatus.FAILED
            prediction_run.error_message = f"Prediction exceeded maximum timeout of {timeout_seconds}s."
            logger.error("Prediction run %s timed out.", run_id)
            await self.prediction_repo.session.commit()
            raise ValidationException(prediction_run.error_message)
            
        except Exception as e:
            prediction_run.status = PredictionStatus.FAILED
            prediction_run.error_message = str(e)
            logger.error("Prediction run %s failed: %s", run_id, e)
            await self.prediction_repo.session.commit()
            raise e

    async def _execute_pipeline_steps(
        self,
        ctx: PredictionPipelineContext,
        run_record: PredictionRun,
        features_list: List[Dict[str, Any]]
    ) -> None:
        # 1. Dependency checks & Active model resolution
        if ctx.model_id:
            model = await self.trained_model_repo.get_by_id(ctx.model_id)
            if not model:
                raise NotFoundException("Specified model was not found.")
        else:
            model = await self.trained_model_repo.get_active_model(ctx.project_id)
            if not model:
                raise NotFoundException("No active model found in the project registry.")
                
        # Link context variables
        ctx.active_model = model
        session = model.training_session
        dataset = session.dataset
        ctx.dataset_id = dataset.id
        ctx.preprocessing_run_id = session.preprocessing_run_id
        ctx.model_version = int(float(model.version)) if model.version.replace(".", "").isdigit() else 1
        ctx.model_checksum = model.checksum or "no_checksum"
        ctx.model_signature_checksum = hashlib.sha256(
            str(model.signature).encode()
        ).hexdigest()
        ctx.dataset_version = dataset.version
        
        # Update PredictionRun audit links
        run_record.model_id = model.id
        run_record.model_version = ctx.model_version
        run_record.model_checksum = ctx.model_checksum
        run_record.model_signature_checksum = ctx.model_signature_checksum
        run_record.dataset_version = ctx.dataset_version
        run_record.preprocessing_run_id = ctx.preprocessing_run_id

        # 2. Features Inputs Validation
        v_start = time.time()
        signature = model.signature or {}
        for features in features_list:
            self.validation_service.validate_features(features, signature)
        ctx.timing_validation = round((time.time() - v_start) * 1000, 2)
        run_record.timing_validation = ctx.timing_validation

        # 3. Model & Preprocessing Artifacts loading (LRU Cache checks)
        l_start = time.time()
        
        # Load estimator using warm cache
        model_key = f"estimator:{model.id}"
        async def load_model():
            return await self.serialization_service.download_and_verify(
                model.storage_path, model.checksum
            )
        estimator = await self.warm_model_cache.get_or_load(model_key, load_model)

        # Load encoders/scalers artifacts
        loaded_transformers = {}
        if dataset.preprocessing_runs:
            # Get completed run
            prep_run = next(
                (pr for pr in dataset.preprocessing_runs if pr.id == ctx.preprocessing_run_id),
                None
            )
            if prep_run:
                for artifact in prep_run.artifacts:
                    art_key = f"artifact:{artifact.id}"
                    
                    async def load_artifact(art=artifact):
                        return await self.serialization_service.download_and_verify(
                            art.storage_path, art.checksum
                        )
                        
                    loaded_transformers[f"{prep_run.id}_{artifact.artifact_type}"] = (
                        await self.warm_model_cache.get_or_load(art_key, load_artifact)
                    )
                    
                    # Also map column specific keys (col_artifact_type)
                    # The artifact path commonly contains column names, e.g. column_scaler.joblib
                    filename = artifact.storage_path.split("/")[-1]
                    if "_" in filename:
                        col_name = filename.split("_")[0]
                        loaded_transformers[f"{col_name}_{artifact.artifact_type}"] = (
                            await self.warm_model_cache.get_or_load(art_key, load_artifact)
                        )
                        
        ctx.timing_loading = round((time.time() - l_start) * 1000, 2)
        run_record.timing_loading = ctx.timing_loading

        # 4. Impute & Transform Feature Data (Chunking processing in groups of 500 rows)
        p_start = time.time()
        
        # Convert all requests to Pandas DataFrame
        raw_df = pd.DataFrame(features_list)
        
        # Setup chunk loops
        chunk_size = 500
        processed_chunks = []
        predictions_all = []
        confidences_all = []
        
        for offset in range(0, len(raw_df), chunk_size):
            chunk_df = raw_df.iloc[offset : offset + chunk_size].copy()
            
            # Impute missing values
            prep_run = next((pr for pr in dataset.preprocessing_runs if pr.id == ctx.preprocessing_run_id), None)
            imputed_df = self.preprocessing_service.impute_missing(chunk_df, dataset, prep_run)
            
            # Transform categories encoding & scaling
            transformed_df = self.preprocessing_service.transform_features(
                imputed_df, prep_run, loaded_transformers
            )
            
            # Reorder columns to match expected signature feature names reorders
            expected_features = signature.get("feature_names", [])
            
            # Handle any generated/one-hot columns in reordering
            # One-hot transforms replace column X with X_cat1, X_cat2, etc.
            # In signature we have the transformed expected feature columns!
            # Let's align features reordering
            for col in expected_features:
                if col not in transformed_df.columns:
                    transformed_df[col] = 0.0 # fallback default values for missing one-hot variables
                    
            aligned_df = transformed_df[expected_features]
            processed_chunks.append(aligned_df)
            
            # 5. Inferencepredict execution
            ind_start = time.time()
            preds, confs = self.inference_service.predict(estimator, aligned_df.to_numpy())
            ctx.timing_prediction += round((time.time() - ind_start) * 1000, 2)
            
            predictions_all.extend(preds)
            if confs:
                if confidences_all is None:
                    confidences_all = []
                confidences_all.extend(confs)
                
        # Combine processed snapshots
        combined_processed = pd.concat(processed_chunks, axis=0)
        
        ctx.timing_preprocessing = round((time.time() - p_start) * 1000 - ctx.timing_prediction, 2)
        run_record.timing_preprocessing = ctx.timing_preprocessing
        run_record.timing_prediction = ctx.timing_prediction
        
        # Write results mapping to PredictionRun
        run_record.preprocessed_features = combined_processed.to_dict(orient="records")
        
        # Format response payload
        prediction_response = {
            "predictions": predictions_all,
            "confidence_scores": confidences_all,
        }
        
        # Optional explainability triggers (placeholders)
        if ctx.include_explanation:
            run_record.explanation_status = "SUCCESS_PLACEHOLDER"
            run_record.explanation_payload = {"shap_explanation": "future_lime_values"}
            run_record.feature_contributions = {"top_features": ["temperature", "water_index"]}
            
        run_record.prediction_response = prediction_response
        
        # Calculate request hash
        ctx.request_hash = self.prediction_cache.compute_request_hash(features_list)
        run_record.request_hash = ctx.request_hash
