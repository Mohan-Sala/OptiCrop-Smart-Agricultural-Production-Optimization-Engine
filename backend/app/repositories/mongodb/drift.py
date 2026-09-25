import uuid
from datetime import datetime
from typing import List, Optional
from app.models.drift_snapshot import DriftSnapshot
from app.core.enums import DriftStatus
from app.repositories.interfaces.drift import DriftRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoDriftRepository(MongoBaseRepository[DriftSnapshot], DriftRepository):
    """Concrete MongoDB / Beanie implementation of DriftRepository."""

    def __init__(self):
        super().__init__(DriftSnapshot)

    async def get_latest_by_model(self, model_id: uuid.UUID) -> Optional[DriftSnapshot]:
        parsed_model_id = to_uuid(model_id)
        return await DriftSnapshot.find_one(
            DriftSnapshot.model_id == parsed_model_id,
            DriftSnapshot.status == DriftStatus.COMPLETED,
            sort=[("-computed_at", 1)],
        )

    async def list_snapshots_by_project(
        self, project_id: uuid.UUID, limit: int = 100
    ) -> List[DriftSnapshot]:
        parsed_project_id = to_uuid(project_id)
        return await DriftSnapshot.find(
            DriftSnapshot.project_id == parsed_project_id
        ).sort("-computed_at").limit(limit).to_list()

    async def prune_snapshots(self, before: datetime, exclude_active_model_ids: List[uuid.UUID]) -> int:
        parsed_excluded = [to_uuid(m_id) for m_id in exclude_active_model_ids]
        result = await DriftSnapshot.find({
            "computed_at": {"$lt": before},
            "model_id": {"$nin": parsed_excluded},
        }).delete()
        return result.deleted_count
