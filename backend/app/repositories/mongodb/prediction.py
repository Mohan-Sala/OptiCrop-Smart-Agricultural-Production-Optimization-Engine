from typing import Any, List, Optional
from app.models.prediction_run import PredictionRun, PredictionStatus
from app.repositories.interfaces.prediction import PredictionRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoPredictionRepository(MongoBaseRepository[PredictionRun], PredictionRepository):
    """Concrete MongoDB / Beanie implementation of PredictionRepository."""

    def __init__(self):
        super().__init__(PredictionRun)

    async def get_by_id(self, id: Any) -> Optional[PredictionRun]:
        parsed_id = to_uuid(id)
        run = await PredictionRun.get(parsed_id)
        if not run and parsed_id != id:
            run = await PredictionRun.get(id)
        return run

    async def get_by_idempotency_key(self, user_id: Any, idempotency_key: str) -> Optional[PredictionRun]:
        parsed_user_id = to_uuid(user_id)
        return await PredictionRun.find_one(
            PredictionRun.user_id == parsed_user_id,
            PredictionRun.idempotency_key == idempotency_key,
            PredictionRun.status == PredictionStatus.COMPLETED,
        )

    async def get_by_request_hash(self, model_id: Any, request_hash: str) -> Optional[PredictionRun]:
        parsed_model_id = to_uuid(model_id)
        return await PredictionRun.find_one(
            PredictionRun.model_id == parsed_model_id,
            PredictionRun.request_hash == request_hash,
            PredictionRun.status == PredictionStatus.COMPLETED,
            sort=[("-created_at", 1)]
        )

    async def list_completed_by_model(self, model_id: Any, limit: int = 500) -> List[PredictionRun]:
        parsed_model_id = to_uuid(model_id)
        return await PredictionRun.find(
            PredictionRun.model_id == parsed_model_id,
            PredictionRun.status == PredictionStatus.COMPLETED,
        ).sort("-prediction_timestamp").limit(limit).to_list()
