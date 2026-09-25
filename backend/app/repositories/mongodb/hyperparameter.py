from typing import Any, Optional
from app.models.hyperparameter_set import HyperparameterSet
from app.repositories.interfaces.hyperparameter import HyperparameterSetRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoHyperparameterSetRepository(MongoBaseRepository[HyperparameterSet], HyperparameterSetRepository):
    """Concrete MongoDB / Beanie implementation of HyperparameterSetRepository."""

    def __init__(self):
        super().__init__(HyperparameterSet)

    async def get_by_model_id(self, model_id: Any) -> Optional[HyperparameterSet]:
        parsed_model_id = to_uuid(model_id)
        return await HyperparameterSet.find_one(
            HyperparameterSet.trained_model_id == parsed_model_id
        )
