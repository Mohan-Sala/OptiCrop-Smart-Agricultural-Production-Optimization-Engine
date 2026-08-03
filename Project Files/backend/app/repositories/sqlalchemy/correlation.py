import uuid
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import select, and_
from app.models.prediction_run import PredictionRun
from app.models.external_telemetry import ExternalTelemetryLog
from app.repositories.interfaces.correlation import CorrelationRepository
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyCorrelationRepository(CorrelationRepository):
    """Concrete SQLAlchemy implementation of CorrelationRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_correlated_dataset(
        self, project_id: uuid.UUID, start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        stmt_runs = select(PredictionRun).where(
            and_(
                PredictionRun.project_id == project_id,
                PredictionRun.prediction_timestamp >= start,
                PredictionRun.prediction_timestamp <= end
            )
        ).order_by(PredictionRun.prediction_timestamp.asc())
        result_runs = await self.session.execute(stmt_runs)
        runs = result_runs.scalars().all()
        
        stmt_tel = select(ExternalTelemetryLog).where(
            and_(
                ExternalTelemetryLog.project_id == project_id,
                ExternalTelemetryLog.recorded_at >= start,
                ExternalTelemetryLog.recorded_at <= end
            )
        ).order_by(ExternalTelemetryLog.recorded_at.asc())
        result_tel = await self.session.execute(stmt_tel)
        telemetries = result_tel.scalars().all()
        
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
