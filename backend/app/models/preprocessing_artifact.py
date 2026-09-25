import uuid
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class PreprocessingArtifact(AppDocument):
    preprocessing_run_id: uuid.UUID
    artifact_type: str
    storage_path: str
    checksum: str

    class Settings:
        name = "preprocessing_artifacts"
        indexes = [
            IndexModel([("preprocessing_run_id", ASCENDING)]),
            IndexModel([("artifact_type", ASCENDING)]),
            IndexModel([("checksum", ASCENDING)]),
        ]
