from typing import Any, List, Dict
from app.models.dataset import Dataset
from app.core.enums import DatasetStage
from app.repositories.interfaces.dataset_analytics import DatasetAnalyticsRepository
from app.repositories.mongodb.base import to_uuid


class MongoDatasetAnalyticsRepository(DatasetAnalyticsRepository):
    """Concrete MongoDB / Beanie implementation of DatasetAnalyticsRepository."""

    def __init__(self):
        pass

    async def get_dataset_stages_distribution(self, project_id: Any) -> Dict[str, int]:
        parsed_project_id = to_uuid(project_id)
        datasets = await Dataset.find(
            Dataset.project_id == parsed_project_id,
            Dataset.is_deleted == False,
        ).to_list()
        dist = {stage.name: 0 for stage in DatasetStage}
        for d in datasets:
            stage_name = d.dataset_stage.name if hasattr(d.dataset_stage, "name") else str(d.dataset_stage)
            if stage_name in dist:
                dist[stage_name] += 1
            else:
                dist[stage_name] = 1
        return dist

    async def get_datasets_growth_history(self, project_id: Any) -> List[Dict[str, Any]]:
        parsed_project_id = to_uuid(project_id)
        datasets = await Dataset.find(
            Dataset.project_id == parsed_project_id,
            Dataset.is_deleted == False,
        ).sort("+created_at").to_list()
        history = []
        for d in datasets:
            history.append({
                "date": d.created_at.isoformat(),
                "size_bytes": d.size,
                "version": d.version,
            })
        return history
