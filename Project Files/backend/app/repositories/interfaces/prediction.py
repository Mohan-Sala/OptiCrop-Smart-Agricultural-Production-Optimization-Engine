from abc import ABC, abstractmethod
from typing import Any, Optional
from app.models.prediction_run import PredictionRun


class PredictionRepository(ABC):
    """Abstract interface for persisting and querying single prediction runs."""

    @abstractmethod
    async def create(self, prediction_run: PredictionRun) -> PredictionRun:
        """Saves a new prediction run audit to database."""
        pass

    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[PredictionRun]:
        """Retrieves prediction run details by unique UUID."""
        pass

    @abstractmethod
    async def get_by_idempotency_key(self, user_id: Any, idempotency_key: str) -> Optional[PredictionRun]:
        """Retrieves previously executed prediction run matching idempotency key and user ID."""
        pass

    @abstractmethod
    async def get_by_request_hash(self, model_id: Any, request_hash: str) -> Optional[PredictionRun]:
        """Retrieves cached prediction matching identical request features and active model."""
        pass

    @abstractmethod
    async def list_completed_by_model(self, model_id: Any, limit: int = 500) -> list[PredictionRun]:
        """Lists completed prediction run logs matching the target model ID."""
        pass
