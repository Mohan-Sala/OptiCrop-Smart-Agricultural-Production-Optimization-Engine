from typing import Any, List, Optional
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.models.dataset import Dataset
from app.repositories.interfaces.training_session import TrainingSessionRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoTrainingSessionRepository(MongoBaseRepository[TrainingSession], TrainingSessionRepository):
    """Concrete MongoDB / Beanie implementation of TrainingSessionRepository."""

    def __init__(self):
        super().__init__(TrainingSession)

    async def _populate_relations(self, session: Optional[TrainingSession]) -> Optional[TrainingSession]:
        if not session:
            return None
        models = await TrainedModel.find(TrainedModel.training_session_id == session.id).to_list()
        session.trained_models = models
        if hasattr(session, "dataset_id") and session.dataset_id:
            dataset = await Dataset.get(session.dataset_id)
            session.dataset = dataset
        return session

    async def get_by_id(self, id: Any) -> Optional[TrainingSession]:
        parsed_id = to_uuid(id)
        session = await TrainingSession.get(parsed_id)
        if not session and parsed_id != id:
            session = await TrainingSession.get(id)
        return await self._populate_relations(session)

    async def get_by_project_id(self, project_id: Any) -> List[TrainingSession]:
        parsed_project_id = to_uuid(project_id)
        # Find all dataset IDs belonging to the project
        datasets = await Dataset.find(
            Dataset.project_id == parsed_project_id,
            Dataset.is_deleted == False,
        ).to_list()
        dataset_ids = [d.id for d in datasets]
        if not dataset_ids:
            return []
        
        sessions = await TrainingSession.find({
            "dataset_id": {"$in": dataset_ids}
        }).sort("-created_at").to_list()

        dataset_map = {d.id: d for d in datasets}
        for s in sessions:
            await self._populate_relations(s)
            s.dataset = dataset_map.get(s.dataset_id)
        return sessions

    async def get_by_hash_and_user(self, config_hash: str, user_id: Any) -> Optional[TrainingSession]:
        parsed_user_id = to_uuid(user_id)
        session = await TrainingSession.find_one(
            TrainingSession.config_hash == config_hash,
            TrainingSession.user_id == parsed_user_id,
            TrainingSession.status == "COMPLETED",
        )
        return await self._populate_relations(session)
