from typing import Any, Optional
from app.models.evaluation_report import EvaluationReport
from app.repositories.interfaces.evaluation import EvaluationReportRepository
from app.repositories.mongodb.base import MongoBaseRepository, to_uuid


class MongoEvaluationReportRepository(MongoBaseRepository[EvaluationReport], EvaluationReportRepository):
    """Concrete MongoDB / Beanie implementation of EvaluationReportRepository."""

    def __init__(self):
        super().__init__(EvaluationReport)

    async def get_by_model_id(self, model_id: Any) -> Optional[EvaluationReport]:
        parsed_model_id = to_uuid(model_id)
        return await EvaluationReport.find_one(
            EvaluationReport.trained_model_id == parsed_model_id
        )
