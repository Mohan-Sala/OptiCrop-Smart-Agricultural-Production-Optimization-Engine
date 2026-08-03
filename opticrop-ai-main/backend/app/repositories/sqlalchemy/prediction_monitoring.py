import uuid
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import select, func, and_, case
from app.models.prediction_run import PredictionRun, PredictionStatus
from app.repositories.interfaces.prediction_monitoring import PredictionMonitoringRepository
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyPredictionMonitoringRepository(PredictionMonitoringRepository):
    """Concrete SQLAlchemy implementation of PredictionMonitoringRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_aggregation_metrics(
        self, project_id: uuid.UUID, start: datetime, end: datetime
    ) -> Dict[str, Any]:
        stmt = select(
            func.count(PredictionRun.id).label("total"),
            func.avg(PredictionRun.execution_time).label("avg_latency"),
            func.sum(case((PredictionRun.status == PredictionStatus.FAILED, 1), else_=0)).label("failures"),
            func.sum(case((PredictionRun.status == PredictionStatus.COMPLETED, 1), else_=0)).label("successes"),
            func.sum(case((PredictionRun.idempotency_key.isnot(None), 1), else_=0)).label("cache_hits"),
        ).where(
            and_(
                PredictionRun.project_id == project_id,
                PredictionRun.prediction_timestamp >= start,
                PredictionRun.prediction_timestamp <= end,
            )
        )
        result = await self.session.execute(stmt)
        row = result.fetchone()
        
        if not row or row[0] is None or row[0] == 0:
            return {
                "total_predictions": 0,
                "success_rate": 100.0,
                "avg_latency_ms": 0.0,
                "cache_hit_ratio": 100.0,
                "failures_count": 0,
            }
            
        total = row[0]
        avg_latency = float(row[1] or 0.0) * 1000.0
        failures = int(row[2] or 0)
        successes = int(row[3] or 0)
        cache_hits = int(row[4] or 0)
        
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
        # For simplicity and vendor-agnostic timeseries grouping, group by date_trunc
        stmt = (
            select(
                func.date_trunc("day", PredictionRun.prediction_timestamp).label("period"),
                func.count(PredictionRun.id).label("total"),
                func.avg(PredictionRun.execution_time).label("avg_latency"),
                func.sum(case((PredictionRun.status == PredictionStatus.FAILED, 1), else_=0)).label("failures"),
            )
            .where(
                and_(
                    PredictionRun.project_id == project_id,
                    PredictionRun.prediction_timestamp >= start,
                    PredictionRun.prediction_timestamp <= end,
                )
            )
            .group_by(func.date_trunc("day", PredictionRun.prediction_timestamp))
            .order_by(func.date_trunc("day", PredictionRun.prediction_timestamp).asc())
        )
        result = await self.session.execute(stmt)
        
        trends = []
        for row in result.all():
            trends.append({
                "period": row[0],
                "prediction_count": int(row[1] or 0),
                "avg_latency_ms": round(float(row[2] or 0.0) * 1000.0, 2),
                "error_count": int(row[3] or 0),
            })
        return trends
