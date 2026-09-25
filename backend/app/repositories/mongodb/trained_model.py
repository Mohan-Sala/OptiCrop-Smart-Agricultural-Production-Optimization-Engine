from typing import Any, List, Optional
from app.models.trained_model import TrainedModel
from app.models.training_session import TrainingSession
from app.models.dataset import Dataset
from app.models.model_metric import ModelMetric
from app.models.evaluation_report import EvaluationReport
from app.models.hyperparameter_set import HyperparameterSet
from app.repositories.interfaces.trained_model import TrainedModelRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoTrainedModelRepository(MongoBaseRepository[TrainedModel], TrainedModelRepository):
    """Concrete MongoDB / Beanie implementation of TrainedModelRepository."""

    def __init__(self):
        super().__init__(TrainedModel)

    async def _populate_relations(self, model: Optional[TrainedModel]) -> Optional[TrainedModel]:
        if not model:
            return None
        model.metrics = await ModelMetric.find(ModelMetric.trained_model_id == model.id).to_list()
        model.evaluation_report = await EvaluationReport.find_one(
            EvaluationReport.trained_model_id == model.id
        )
        model.hyperparameter_set = await HyperparameterSet.find_one(
            HyperparameterSet.trained_model_id == model.id
        )
        session = await TrainingSession.get(model.training_session_id)
        if session:
            dataset = await Dataset.get(session.dataset_id)
            session.dataset = dataset
            model.training_session = session
        return model

    async def get_by_id(self, id: Any) -> Optional[TrainedModel]:
        parsed_id = to_uuid(id)
        model = await TrainedModel.get(parsed_id)
        if not model and parsed_id != id:
            model = await TrainedModel.get(id)
        return await self._populate_relations(model)

    async def _get_project_training_session_ids(self, project_id: Any) -> List[Any]:
        parsed_project_id = to_uuid(project_id)
        datasets = await Dataset.find(
            Dataset.project_id == parsed_project_id,
            Dataset.is_deleted == False,
        ).to_list()
        dataset_ids = [d.id for d in datasets]
        if not dataset_ids:
            return []
        sessions = await TrainingSession.find({"dataset_id": {"$in": dataset_ids}}).to_list()
        return [s.id for s in sessions]

    async def get_by_project_id(self, project_id: Any) -> List[TrainedModel]:
        session_ids = await self._get_project_training_session_ids(project_id)
        if not session_ids:
            return []
        models = await TrainedModel.find({
            "training_session_id": {"$in": session_ids}
        }).sort("-created_at").to_list()
        for m in models:
            await self._populate_relations(m)
        return models

    async def get_active_model(self, project_id: Any) -> Optional[TrainedModel]:
        session_ids = await self._get_project_training_session_ids(project_id)
        if not session_ids:
            return None
        model = await TrainedModel.find_one({
            "training_session_id": {"$in": session_ids},
            "is_active": True,
        })
        return await self._populate_relations(model)

    async def deactivate_all_in_project(self, project_id: Any) -> None:
        session_ids = await self._get_project_training_session_ids(project_id)
        if session_ids:
            await TrainedModel.find({
                "training_session_id": {"$in": session_ids}
            }).update({"$set": {"is_active": False}})
