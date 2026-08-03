import abc
import uuid
from datetime import datetime
from typing import List, Optional
from app.models.monitoring_alert import MonitoringAlert
from app.models.alert_rule import AlertRule
from app.repositories.interfaces.base import BaseRepository


class AlertRepository(BaseRepository[MonitoringAlert], metaclass=abc.ABCMeta):
    """Abstract interface for monitoring alert rules and triggered alerts logs."""

    @abc.abstractmethod
    async def get_rule_by_id(self, rule_id: uuid.UUID) -> Optional[AlertRule]:
        pass

    @abc.abstractmethod
    async def list_rules_by_project(self, project_id: uuid.UUID) -> List[AlertRule]:
        pass

    @abc.abstractmethod
    async def create_rule(self, rule: AlertRule) -> AlertRule:
        pass

    @abc.abstractmethod
    async def get_active_alert_for_rule(
        self, project_id: uuid.UUID, model_id: uuid.UUID, rule_id: uuid.UUID, severity: str
    ) -> Optional[MonitoringAlert]:
        pass

    @abc.abstractmethod
    async def list_alerts_by_project(
        self, project_id: uuid.UUID, status: Optional[str] = None
    ) -> List[MonitoringAlert]:
        pass

    @abc.abstractmethod
    async def prune_resolved_alerts(self, before: datetime) -> int:
        pass
