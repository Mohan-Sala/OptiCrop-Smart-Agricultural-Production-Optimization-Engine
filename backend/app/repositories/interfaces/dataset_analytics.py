from abc import ABC, abstractmethod
from typing import Any, List, Dict


class DatasetAnalyticsRepository(ABC):
    """Abstract interface for aggregating dataset-specific analytics."""

    @abstractmethod
    async def get_dataset_stages_distribution(self, project_id: Any) -> Dict[str, int]:
        """Returns distribution of datasets across RAW, PREPROCESSED, FEATURE_ENGINEERED, READY_FOR_TRAINING stages."""
        pass

    @abstractmethod
    async def get_datasets_growth_history(self, project_id: Any) -> List[Dict[str, Any]]:
        """Returns datasets creation timelines mapping size and version counts."""
        pass
