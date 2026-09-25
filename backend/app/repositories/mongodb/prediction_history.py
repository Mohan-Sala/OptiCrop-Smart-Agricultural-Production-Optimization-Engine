from typing import Any, List, Optional
from app.models.prediction_run import PredictionRun
from app.repositories.interfaces.prediction_history import PredictionHistoryRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoPredictionHistoryRepository(MongoBaseRepository[PredictionRun], PredictionHistoryRepository):
    """Concrete MongoDB / Beanie implementation of PredictionHistoryRepository."""

    def __init__(self):
        super().__init__(PredictionRun)

    async def list_history_paginated(
        self,
        user_id: Any,
        project_id: Optional[Any] = None,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
    ) -> List[PredictionRun]:
        parsed_user_id = to_uuid(user_id)
        query: dict = {"user_id": parsed_user_id}

        if project_id is not None:
            query["project_id"] = to_uuid(project_id)
        if status is not None:
            query["status"] = status

        offset = (page - 1) * page_size
        return await PredictionRun.find(query).sort("-created_at").skip(offset).limit(page_size).to_list()
