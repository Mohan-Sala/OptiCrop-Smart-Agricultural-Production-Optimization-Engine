import time
import asyncio
import logging
from typing import Any, Dict, Optional, Tuple, List
from app.services.monitoring.event_bus import EventBus

logger = logging.getLogger("app.services.monitoring.cache")


class MonitoringCache:
    """Event-driven cache subscribing to data modifications to trigger automatic key invalidations."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._register_event_subscribers()

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            val, expire = self._cache[key]
            if time.time() < expire:
                return val
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        self._cache[key] = (value, time.time() + ttl_seconds)

    def evict(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        self._cache.clear()

    def _register_event_subscribers(self) -> None:
        async def on_prediction_completed(msg: Any):
            logger.info("Received event: PredictionCompleted, evicting project caches.")
            self._invalidate_project_keys(msg.get("project_id"))

        async def on_telemetry_ingested(msg: Any):
            logger.info("Received event: TelemetryIngested, evicting cache.")
            self._invalidate_project_keys(msg.get("project_id"))

        async def on_model_activated(msg: Any):
            logger.info("Received event: ModelActivated, evicting cache.")
            self._invalidate_project_keys(msg.get("project_id"))
            self.evict(f"monitoring:drift:{msg.get('model_id')}")

        async def on_training_completed(msg: Any):
            logger.info("Received event: TrainingCompleted.")
            self._invalidate_project_keys(msg.get("project_id"))

        async def on_dataset_deleted(msg: Any):
            logger.info("Received event: DatasetDeleted.")
            self.clear()

        async def on_alert_acknowledged(msg: Any):
            logger.info("Received event: AlertAcknowledged.")
            self._invalidate_project_keys(msg.get("project_id"))

        self.event_bus.subscribe("PredictionCompleted", on_prediction_completed)
        self.event_bus.subscribe("TelemetryIngested", on_telemetry_ingested)
        self.event_bus.subscribe("ModelActivated", on_model_activated)
        self.event_bus.subscribe("TrainingCompleted", on_training_completed)
        self.event_bus.subscribe("DatasetDeleted", on_dataset_deleted)
        self.event_bus.subscribe("AlertAcknowledged", on_alert_acknowledged)

    def _invalidate_project_keys(self, project_id: Optional[str]) -> None:
        if not project_id:
            return
        p_id = str(project_id)
        keys_to_del = [
            "monitoring:overview",
            f"monitoring:project:{p_id}:day",
            f"monitoring:project:{p_id}:week",
            f"monitoring:project:{p_id}:month",
        ]
        for k in keys_to_del:
            self.evict(k)
