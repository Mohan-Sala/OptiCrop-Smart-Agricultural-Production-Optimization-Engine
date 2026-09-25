from typing import Any, List, Optional, Tuple
from app.models.dataset import Dataset
from app.repositories.interfaces.dataset import DatasetRepository
from app.repositories.mongodb.dataset import MongoDatasetRepository


class SqlAlchemyDatasetRepository(MongoDatasetRepository):
    """Compatibility adapter redirecting legacy SqlAlchemyDatasetRepository to MongoDatasetRepository."""

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
