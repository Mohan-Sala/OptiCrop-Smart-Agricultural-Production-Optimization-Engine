from datetime import datetime
from typing import List
from app.models.monitoring_health_log import MonitoringHealthLog
from app.repositories.interfaces.health import HealthRepository
from app.repositories.mongodb.base import MongoBaseRepository


class MongoHealthRepository(MongoBaseRepository[MonitoringHealthLog], HealthRepository):
    """Concrete MongoDB / Beanie implementation of HealthRepository."""

    def __init__(self):
        super().__init__(MonitoringHealthLog)

    async def list_health_history(self, limit: int = 100) -> List[MonitoringHealthLog]:
        return await MonitoringHealthLog.find().sort("-recorded_at").limit(limit).to_list()

    async def prune_health_logs(self, before: datetime) -> int:
        result = await MonitoringHealthLog.find(
            MonitoringHealthLog.recorded_at < before
        ).delete()
        return result.deleted_count
