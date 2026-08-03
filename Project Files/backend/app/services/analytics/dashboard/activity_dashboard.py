import uuid
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import Dataset
from app.models.training_session import TrainingSession


class ActivityDashboardService:
    """Aggregates chronological action history feeds for datasets, preprocessing, and training milestones."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_recent_activity(self, project_id: uuid.UUID, limit: int = 5) -> List[Dict[str, Any]]:
        ds_stmt = (
            select(Dataset.name, Dataset.dataset_stage, Dataset.created_at)
            .where(Dataset.project_id == project_id, Dataset.is_deleted == False)
            .order_by(Dataset.created_at.desc())
            .limit(limit)
        )
        ds_res = await self.session.execute(ds_stmt)
        activities = []
        for name, stage, created_at in ds_res.all():
            activities.append({
                "activity_type": "dataset_action",
                "message": f"Dataset '{name}' registered at stage {stage.name if hasattr(stage, 'name') else str(stage)}.",
                "timestamp": created_at
            })
            
        sess_stmt = (
            select(TrainingSession.best_model, TrainingSession.status, TrainingSession.created_at)
            .join(TrainingSession.dataset)
            .where(Dataset.project_id == project_id)
            .order_by(TrainingSession.created_at.desc())
            .limit(limit)
        )
        sess_res = await self.session.execute(sess_stmt)
        for best_model, status, created_at in sess_res.all():
            model_name = best_model or "Model search"
            activities.append({
                "activity_type": "training_action",
                "message": f"{model_name} session status transitioned to {status.upper()}.",
                "timestamp": created_at
            })
            
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Format timestamps to iso strings for serialization
        formatted_activities = []
        for act in activities[:limit]:
            formatted_activities.append({
                "activity_type": act["activity_type"],
                "message": act["message"],
                "timestamp": act["timestamp"].isoformat() if hasattr(act["timestamp"], "isoformat") else str(act["timestamp"])
            })
            
        return formatted_activities
