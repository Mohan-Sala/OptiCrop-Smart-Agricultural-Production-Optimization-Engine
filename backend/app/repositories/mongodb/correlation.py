import uuid
from datetime import datetime
from typing import List, Dict, Any
from app.models.prediction_run import PredictionRun
from app.models.external_telemetry import ExternalTelemetryLog
from app.repositories.interfaces.correlation import CorrelationRepository
from app.repositories.mongodb.base import to_uuid


class MongoCorrelationRepository(CorrelationRepository):
    """Concrete MongoDB / Beanie implementation of CorrelationRepository."""

    def __init__(self):
        pass

    async def get_correlated_dataset(
        self, project_id: uuid.UUID, start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        parsed_project_id = to_uuid(project_id)
        runs = await PredictionRun.find({
            "project_id": parsed_project_id,
            "prediction_timestamp": {"$gte": start, "$lte": end},
        }).sort("+prediction_timestamp").to_list()

        telemetries = await ExternalTelemetryLog.find({
            "project_id": parsed_project_id,
            "recorded_at": {"$gte": start, "$lte": end},
        }).sort("+recorded_at").to_list()

        correlated = []
        for r in runs:
            closest_t = None
            min_diff = 3600.0

            for t in telemetries:
                diff = abs((r.prediction_timestamp - t.recorded_at).total_seconds())
                if diff < min_diff:
                    min_diff = diff
                    closest_t = t

            correlated.append({
                "prediction_id": r.id,
                "prediction_timestamp": r.prediction_timestamp,
                "predictions": r.prediction_response.get("predictions", []) if r.prediction_response else [],
                "feature_contributions": r.feature_contributions,
                "telemetry": closest_t.normalized_payload if closest_t else None,
                "telemetry_recorded_at": closest_t.recorded_at if closest_t else None,
            })

        return correlated
