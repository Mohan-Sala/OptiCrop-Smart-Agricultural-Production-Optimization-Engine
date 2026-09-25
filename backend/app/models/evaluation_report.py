import uuid
from typing import Dict, Any
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class EvaluationReport(AppDocument):
    trained_model_id: uuid.UUID
    report_data: Dict[str, Any]

    class Settings:
        name = "evaluation_reports"
        indexes = [
            IndexModel([("trained_model_id", ASCENDING)]),
        ]
