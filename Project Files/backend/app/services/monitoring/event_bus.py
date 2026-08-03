import abc
import asyncio
import logging
from typing import Callable, Any, Dict, List

logger = logging.getLogger("app.services.monitoring.event_bus")


class EventBus(abc.ABC):
    """Abstract event bus interface for future distributed message integrations (NATS/RabbitMQ)."""

    @abc.abstractmethod
    async def publish(self, topic: str, message: Any) -> None:
        pass

    @abc.abstractmethod
    def subscribe(self, topic: str, handler: Callable[[Any], None]) -> None:
        pass


class InProcessEventBus(EventBus):
    """Simple in-memory thread-safe event bus dispatcher for decoupling monitoring workflows."""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    async def publish(self, topic: str, message: Any) -> None:
        logger.info("Publishing event to topic '%s': %s", topic, message)
        if topic in self._handlers:
            for handler in self._handlers[topic]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message)
                    else:
                        handler(message)
                except Exception as e:
                    logger.error("Handler error on topic '%s': %s", topic, e)

    def subscribe(self, topic: str, handler: Callable[[Any], None]) -> None:
        if topic not in self._handlers:
            self._handlers[topic] = []
        self._handlers[topic].append(handler)
