import uuid
from datetime import datetime
from typing import List, Dict, Any
from app.repositories.interfaces.correlation import CorrelationRepository


class CorrelationService:
    """Service correlating external telemetry with prediction logs and features importance."""

    def __init__(self, correlation_repo: CorrelationRepository):
        self.correlation_repo = correlation_repo

    async def get_aligned_diagnostics(
        self, project_id: uuid.UUID, start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        return await self.correlation_repo.get_correlated_dataset(project_id, start, end)
