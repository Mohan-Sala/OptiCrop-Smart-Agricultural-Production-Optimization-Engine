import uuid
from typing import List, Optional, Any
from app.models.prediction_run import PredictionRun
from app.repositories.interfaces.prediction_history import PredictionHistoryRepository


class PredictionHistoryService:
    """Manages prediction audit logs and execution histories list operations."""

    def __init__(self, history_repo: PredictionHistoryRepository):
        self.history_repo = history_repo

    async def list_runs(
        self,
        user_id: Any,
        project_id: Optional[uuid.UUID] = None,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
    ) -> List[PredictionRun]:
        return await self.history_repo.list_history_paginated(
            user_id=user_id,
            project_id=project_id,
            page=page,
            page_size=page_size,
            status=status
        )
