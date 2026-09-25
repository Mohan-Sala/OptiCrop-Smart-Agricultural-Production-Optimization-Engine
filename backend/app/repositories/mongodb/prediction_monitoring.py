import uuid
from datetime import datetime
from typing import Dict, Any, List
from app.models.prediction_run import PredictionRun, PredictionStatus
from app.repositories.interfaces.prediction_monitoring import PredictionMonitoringRepository
from app.repositories.mongodb.base import to_uuid


class MongoPredictionMonitoringRepository(PredictionMonitoringRepository):
    """Concrete MongoDB / Beanie implementation of PredictionMonitoringRepository."""

    def __init__(self):
        pass

    async def get_aggregation_metrics(
        self, project_id: uuid.UUID, start: datetime, end: datetime
    ) -> Dict[str, Any]:
        parsed_project_id = to_uuid(project_id)
        runs = await PredictionRun.find({
            "project_id": parsed_project_id,
            "prediction_timestamp": {"$gte": start, "$lte": end},
        }).to_list()

        if not runs:
            return {
                "total_predictions": 0,
                "success_rate": 100.0,
                "avg_latency_ms": 0.0,
                "cache_hit_ratio": 100.0,
                "failures_count": 0,
            }

        total = len(runs)
        total_latency = sum(r.execution_time for r in runs)
        avg_latency = (total_latency / total) * 1000.0
        failures = sum(1 for r in runs if r.status == PredictionStatus.FAILED)
        successes = sum(1 for r in runs if r.status == PredictionStatus.COMPLETED)
        cache_hits = sum(1 for r in runs if r.idempotency_key is not None)

        success_rate = (successes / total) * 100.0 if total > 0 else 100.0
        cache_hit_ratio = (cache_hits / total) * 100.0 if total > 0 else 100.0

        return {
            "total_predictions": total,
            "success_rate": round(success_rate, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "cache_hit_ratio": round(cache_hit_ratio, 2),
            "failures_count": failures,
        }

    async def get_latency_trends(
        self, project_id: uuid.UUID, start: datetime, end: datetime, interval_hours: int = 24
    ) -> List[Dict[str, Any]]:
        parsed_project_id = to_uuid(project_id)
        runs = await PredictionRun.find({
            "project_id": parsed_project_id,
            "prediction_timestamp": {"$gte": start, "$lte": end},
        }).sort("+prediction_timestamp").to_list()

        grouped: Dict[str, list[PredictionRun]] = {}
        for r in runs:
            day_key = r.prediction_timestamp.strftime("%Y-%m-%d")
            grouped.setdefault(day_key, []).append(r)

        trends = []
        for period in sorted(grouped.keys()):
            group = grouped[period]
            total = len(group)
            avg_latency = (sum(r.execution_time for r in group) / total) * 1000.0 if total > 0 else 0.0
            error_count = sum(1 for r in group if r.status == PredictionStatus.FAILED)
            trends.append({
                "period": period,
                "prediction_count": total,
                "avg_latency_ms": round(avg_latency, 2),
                "error_count": error_count,
            })
        return trends
