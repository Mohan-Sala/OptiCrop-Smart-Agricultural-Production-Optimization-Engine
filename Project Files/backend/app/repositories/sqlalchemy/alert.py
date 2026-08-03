import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, delete, and_
from app.models.monitoring_alert import MonitoringAlert
from app.models.alert_rule import AlertRule
from app.core.enums import AlertStatus
from app.repositories.interfaces.alert import AlertRepository
from app.repositories.sqlalchemy.base import SqlAlchemyBaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyAlertRepository(SqlAlchemyBaseRepository[MonitoringAlert], AlertRepository):
    """Concrete SQLAlchemy implementation of AlertRepository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, MonitoringAlert)

    async def get_rule_by_id(self, rule_id: uuid.UUID) -> Optional[AlertRule]:
        stmt = select(AlertRule).where(AlertRule.id == rule_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_rules_by_project(self, project_id: uuid.UUID) -> List[AlertRule]:
        stmt = select(AlertRule).where(AlertRule.project_id == project_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_rule(self, rule: AlertRule) -> AlertRule:
        self.session.add(rule)
        await self.session.flush()
        return rule

    async def get_active_alert_for_rule(
        self, project_id: uuid.UUID, model_id: uuid.UUID, rule_id: uuid.UUID, severity: str
    ) -> Optional[MonitoringAlert]:
        stmt = select(MonitoringAlert).where(
            and_(
                MonitoringAlert.project_id == project_id,
                MonitoringAlert.model_id == model_id,
                MonitoringAlert.rule_id == rule_id,
                MonitoringAlert.severity == severity,
                MonitoringAlert.status == AlertStatus.ACTIVE,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_alerts_by_project(
        self, project_id: uuid.UUID, status: Optional[str] = None
    ) -> List[MonitoringAlert]:
        stmt = select(MonitoringAlert).where(MonitoringAlert.project_id == project_id)
        if status:
            stmt = stmt.where(MonitoringAlert.status == status)
        stmt = stmt.order_by(MonitoringAlert.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def prune_resolved_alerts(self, before: datetime) -> int:
        stmt = delete(MonitoringAlert).where(
            and_(
                MonitoringAlert.status == AlertStatus.RESOLVED,
                MonitoringAlert.resolved_at < before,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount
