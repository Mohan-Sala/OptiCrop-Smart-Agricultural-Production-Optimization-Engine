import abc
import uuid
from datetime import datetime
from typing import List, Dict, Any


class CorrelationRepository(metaclass=abc.ABCMeta):
    """Abstract interface for correlating telemetry sensor values with prediction outputs."""

    @abc.abstractmethod
    async def get_correlated_dataset(
        self, project_id: uuid.UUID, start: datetime, end: datetime
    ) -> List[Dict[str, Any]]:
        """Joins historical prediction preprocessed features vectors with external telemetry records."""
        pass
