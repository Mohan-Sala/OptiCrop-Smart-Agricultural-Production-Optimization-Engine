from abc import ABC, abstractmethod
from typing import Any, List, Optional
from app.models.prediction_run import PredictionRun


class PredictionHistoryRepository(ABC):
    """Abstract interface for retrieving paginated historical logs of prediction runs."""

    @abstractmethod
    async def list_history_paginated(
        self,
        user_id: Any,
        project_id: Optional[Any] = None,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
    ) -> List[PredictionRun]:
        """Lists historical prediction runs filtered and paginated."""
        pass
