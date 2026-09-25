from typing import Any, List
from app.models.trained_model import TrainedModel
from app.models.training_session import TrainingSession
from app.models.dataset import Dataset
from app.models.model_metric import ModelMetric
from app.models.evaluation_report import EvaluationReport
from app.models.hyperparameter_set import HyperparameterSet
from app.repositories.interfaces.comparison_analytics import ComparisonAnalyticsRepository
from app.repositories.mongodb.base import to_uuid


class MongoComparisonAnalyticsRepository(ComparisonAnalyticsRepository):
    """Concrete MongoDB / Beanie implementation of ComparisonAnalyticsRepository."""

    def __init__(self):
        pass

    async def get_models_by_ids(self, model_ids: List[Any]) -> List[TrainedModel]:
        parsed_ids = [to_uuid(m_id) for m_id in model_ids]
        models = await TrainedModel.find({"_id": {"$in": parsed_ids}}).to_list()
        for m in models:
            m.metrics = await ModelMetric.find(ModelMetric.trained_model_id == m.id).to_list()
            m.evaluation_report = await EvaluationReport.find_one(
                EvaluationReport.trained_model_id == m.id
            )
            m.hyperparameter_set = await HyperparameterSet.find_one(
                HyperparameterSet.trained_model_id == m.id
            )
            session = await TrainingSession.get(m.training_session_id)
            if session:
                dataset = await Dataset.get(session.dataset_id)
                session.dataset = dataset
                m.training_session = session
        return models
