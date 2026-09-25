from typing import Any, List
from app.models.prediction_run import PredictionRun
from app.repositories.interfaces.prediction_audit import PredictionAuditRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoPredictionAuditRepository(MongoBaseRepository[PredictionRun], PredictionAuditRepository):
    """Concrete MongoDB / Beanie implementation of PredictionAuditRepository."""

    def __init__(self):
        super().__init__(PredictionRun)

    async def get_system_audit_metrics(self, project_id: Any) -> List[PredictionRun]:
        parsed_project_id = to_uuid(project_id)
        return await PredictionRun.find(
            PredictionRun.project_id == parsed_project_id
        ).sort("-created_at").to_list()
