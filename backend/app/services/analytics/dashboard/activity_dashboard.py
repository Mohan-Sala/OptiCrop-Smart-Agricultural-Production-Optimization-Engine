import uuid
from typing import Dict, Any, List
from app.models.dataset import Dataset
from app.models.training_session import TrainingSession
from app.repositories.mongodb.base import to_uuid


class ActivityDashboardService:
    """Aggregates chronological action history feeds for datasets, preprocessing, and training milestones."""

    def __init__(self, session=None):
        pass

    async def get_recent_activity(self, project_id: uuid.UUID, limit: int = 5) -> List[Dict[str, Any]]:
        parsed_project_id = to_uuid(project_id)
        datasets = await Dataset.find(
            Dataset.project_id == parsed_project_id,
            Dataset.is_deleted == False,
        ).sort("-created_at").limit(limit).to_list()

        activities = []
        for d in datasets:
            stage_name = d.dataset_stage.name if hasattr(d.dataset_stage, "name") else str(d.dataset_stage)
            activities.append({
                "activity_type": "dataset_action",
                "message": f"Dataset '{d.name}' registered at stage {stage_name}.",
                "timestamp": d.created_at,
            })

        all_project_datasets = await Dataset.find(
            Dataset.project_id == parsed_project_id,
            Dataset.is_deleted == False,
        ).to_list()
        dataset_ids = [d.id for d in all_project_datasets]

        if dataset_ids:
            sessions = await TrainingSession.find({
                "dataset_id": {"$in": dataset_ids}
            }).sort("-created_at").limit(limit).to_list()

            for s in sessions:
                model_name = s.best_model or "Model search"
                status_str = s.status.upper() if s.status else "PENDING"
                activities.append({
                    "activity_type": "training_action",
                    "message": f"{model_name} session status transitioned to {status_str}.",
                    "timestamp": s.created_at,
                })

        activities.sort(key=lambda x: x["timestamp"], reverse=True)

        formatted_activities = []
        for act in activities[:limit]:
            formatted_activities.append({
                "activity_type": act["activity_type"],
                "message": act["message"],
                "timestamp": act["timestamp"].isoformat() if hasattr(act["timestamp"], "isoformat") else str(act["timestamp"]),
            })

        return formatted_activities
