import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy import select, and_
from app.models.monitoring_alert import MonitoringAlert
from app.models.alert_rule import AlertRule
from app.core.enums import AlertStatus
from app.repositories.interfaces.alert import AlertRepository
from app.utils.exceptions import ValidationException

logger = logging.getLogger("app.services.monitoring.alerts")


class AlertsService:
    """Evaluates metrics boundaries and raises/deduplicates active system alerts."""

    def __init__(self, alert_repo: AlertRepository):
        self.alert_repo = alert_repo

    async def evaluate_and_trigger(
        self,
        project_id: uuid.UUID,
        model_id: uuid.UUID,
        rule: AlertRule,
        current_value: float,
        message: str,
        severity: str = "WARNING",
    ) -> Optional[MonitoringAlert]:
        is_triggered = False
        op = rule.comparison_operator
        if op == ">" and current_value > rule.threshold_value:
            is_triggered = True
        elif op == "<" and current_value < rule.threshold_value:
            is_triggered = True
        elif op == ">=" and current_value >= rule.threshold_value:
            is_triggered = True
        elif op == "<=" and current_value <= rule.threshold_value:
            is_triggered = True
            
        if not is_triggered:
            return None

        time_window = datetime.utcnow() - timedelta(hours=1)
        existing = await self.alert_repo.get_active_alert_for_rule(project_id, model_id, rule.id, severity)
        
        if existing and existing.last_triggered_at >= time_window:
            existing.occurrence_count += 1
            existing.last_triggered_at = datetime.utcnow()
            existing.metric_value = current_value
            await self.alert_repo.session.flush()
            logger.info("Deduplicated alert rule '%s' triggered. Count = %s", rule.metric_name, existing.occurrence_count)
            return existing
            
        alert = MonitoringAlert(
            project_id=project_id,
            model_id=model_id,
            rule_id=rule.id,
            rule_name=rule.metric_name,
            severity=severity,
            message=message,
            metric_value=current_value,
            threshold_value=rule.threshold_value,
            status=AlertStatus.ACTIVE,
            occurrence_count=1,
            last_triggered_at=datetime.utcnow(),
        )
        await self.alert_repo.create(alert)
        await self.alert_repo.session.flush()
        logger.info("Raised new alert for rule '%s' (value: %s)", rule.metric_name, current_value)
        return alert

    async def acknowledge_alert(self, alert_id: uuid.UUID, user_id: uuid.UUID) -> Optional[MonitoringAlert]:
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            return None
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = user_id
        await self.alert_repo.session.flush()
        return alert

    async def resolve_alert(self, alert_id: uuid.UUID, user_id: uuid.UUID) -> Optional[MonitoringAlert]:
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            return None
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = user_id
        await self.alert_repo.session.flush()
        return alert
