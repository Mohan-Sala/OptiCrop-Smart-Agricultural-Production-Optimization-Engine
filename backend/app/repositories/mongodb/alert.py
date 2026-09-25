import uuid
from datetime import datetime
from typing import List, Optional
from app.models.monitoring_alert import MonitoringAlert
from app.models.alert_rule import AlertRule
from app.core.enums import AlertStatus
from app.repositories.interfaces.alert import AlertRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoAlertRepository(MongoBaseRepository[MonitoringAlert], AlertRepository):
    """Concrete MongoDB / Beanie implementation of AlertRepository."""

    def __init__(self, *args, **kwargs):
        super().__init__(MonitoringAlert, *args, **kwargs)

    async def get_rule_by_id(self, rule_id: uuid.UUID) -> Optional[AlertRule]:
        parsed_id = to_uuid(rule_id)
        return await AlertRule.get(parsed_id)

    async def list_rules_by_project(self, project_id: uuid.UUID) -> List[AlertRule]:
        parsed_id = to_uuid(project_id)
        return await AlertRule.find(AlertRule.project_id == parsed_id).to_list()

    async def create_rule(self, rule: AlertRule) -> AlertRule:
        await rule.insert()
        return rule

    async def get_active_alert_for_rule(
        self, project_id: uuid.UUID, model_id: uuid.UUID, rule_id: uuid.UUID, severity: str
    ) -> Optional[MonitoringAlert]:
        return await MonitoringAlert.find_one(
            MonitoringAlert.project_id == to_uuid(project_id),
            MonitoringAlert.model_id == to_uuid(model_id),
            MonitoringAlert.rule_id == to_uuid(rule_id),
            MonitoringAlert.severity == severity,
            MonitoringAlert.status == AlertStatus.ACTIVE,
        )

    async def list_alerts_by_project(
        self, project_id: uuid.UUID, status: Optional[str] = None
    ) -> List[MonitoringAlert]:
        query: dict = {"project_id": to_uuid(project_id)}
        if status:
            query["status"] = status
        return await MonitoringAlert.find(query).sort("-created_at").to_list()

    async def prune_resolved_alerts(self, before: datetime) -> int:
        result = await MonitoringAlert.find({
            "status": AlertStatus.RESOLVED,
            "resolved_at": {"$lt": before},
        }).delete()
        return result.deleted_count
