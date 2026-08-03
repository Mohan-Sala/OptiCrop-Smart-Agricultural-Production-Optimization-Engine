import uuid
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from app.repositories.interfaces.drift import DriftRepository
from app.repositories.interfaces.prediction import PredictionRepository
from app.repositories.interfaces.trained_model import TrainedModelRepository
from app.services.monitoring.drift_algorithms import DriftAlgorithmRegistry
from app.models.drift_snapshot import DriftSnapshot
from app.core.enums import DriftStatus
from app.utils.exceptions import NotFoundException

logger = logging.getLogger("app.services.monitoring.drift")


class DriftService:
    """Orchestrates feature data drift calculations comparing training vs inference populations."""

    def __init__(
        self,
        drift_repo: DriftRepository,
        trained_model_repo: TrainedModelRepository,
        prediction_repo: PredictionRepository,
        algorithm_registry: DriftAlgorithmRegistry
    ):
        self.drift_repo = drift_repo
        self.trained_model_repo = trained_model_repo
        self.prediction_repo = prediction_repo
        self.algorithm_registry = algorithm_registry

    async def calculate_drift(
        self, model_id: uuid.UUID, algorithm_name: str = "PSI", params: Optional[Dict[str, Any]] = None
    ) -> DriftSnapshot:
        if params is None:
            params = {}

        model = await self.trained_model_repo.get_by_id(model_id)
        if not model:
            raise NotFoundException("Trained model not found.")

        session_rec = model.training_session
        dataset = session_rec.dataset
        stats = dataset.statistics
        col_summary = stats.column_summary if stats else {}
        baseline_version = stats.id.hex if stats else "v1"

        snapshot = DriftSnapshot(
            project_id=dataset.project_id,
            model_id=model_id,
            method_name=algorithm_name,
            drift_score=0.0,
            is_drifted=False,
            feature_drifts={},
            baseline_statistics_version=baseline_version,
            algorithm_version="1.0",
            status=DriftStatus.PENDING,
        )
        await self.drift_repo.create(snapshot)
        await self.drift_repo.session.flush()

        try:
            snapshot.status = DriftStatus.RUNNING
            await self.drift_repo.session.flush()

            runs = await self.prediction_repo.list_completed_by_model(model_id, limit=500)
            if not runs:
                snapshot.status = DriftStatus.COMPLETED
                snapshot.drift_score = 0.0
                snapshot.is_drifted = False
                snapshot.feature_drifts = {}
                await self.drift_repo.session.flush()
                return snapshot

            algorithm = self.algorithm_registry.get(algorithm_name)
            
            feature_drifts_meta = {}
            overall_drift = False
            total_drift_score = 0.0
            computed_features_count = 0
            
            expected_features = model.signature.get("feature_names", []) if model.signature else []
            
            for feature in expected_features:
                feat_stats = col_summary.get(feature, {})
                baseline_mean = feat_stats.get("mean", 0.0)
                baseline_std = feat_stats.get("std", 1.0)
                
                current_values = []
                for r in runs:
                    if r.preprocessed_features:
                        for row in r.preprocessed_features:
                            val = row.get(feature)
                            if val is not None:
                                current_values.append(float(val))
                                
                if len(current_values) < 5:
                    continue
                    
                baseline_arr = np.random.normal(baseline_mean, baseline_std, len(current_values))
                current_arr = np.array(current_values)
                
                res = algorithm.compute_drift(baseline_arr, current_arr, params)
                score = res["drift_score"]
                detected = res["drift_detected"]
                
                feature_drifts_meta[feature] = {
                    "feature_name": feature,
                    "baseline_mean": float(baseline_mean),
                    "baseline_std": float(baseline_std),
                    "current_mean": float(current_arr.mean()),
                    "current_std": float(current_arr.std()),
                    "drift_score": float(score),
                    "drift_detected": bool(detected),
                    "importance_rank": None
                }
                
                total_drift_score += score
                computed_features_count += 1
                if detected:
                    overall_drift = True

            avg_drift_score = total_drift_score / computed_features_count if computed_features_count > 0 else 0.0
            
            snapshot.drift_score = avg_drift_score
            snapshot.is_drifted = overall_drift
            snapshot.feature_drifts = feature_drifts_meta
            snapshot.status = DriftStatus.COMPLETED
            await self.drift_repo.session.flush()
            
            return snapshot
            
        except Exception as e:
            snapshot.status = DriftStatus.FAILED
            snapshot.error_message = str(e)
            await self.drift_repo.session.flush()
            raise e
