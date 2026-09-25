import uuid
from typing import Optional
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from app.models.base import AppDocument


class FeatureMetadata(AppDocument):
    dataset_id: uuid.UUID
    feature_name: str
    feature_type: str  # NUMERIC, CATEGORICAL, TARGET
    
    nullable: bool = False
    encoded: bool = False
    scaled: bool = False
    generated: bool = False
    target: bool = False

    class Settings:
        name = "feature_metadata"
        indexes = [
            IndexModel([("dataset_id", ASCENDING)]),
            IndexModel([("dataset_id", ASCENDING), ("feature_name", ASCENDING)]),
            IndexModel([("feature_type", ASCENDING)]),
            IndexModel([("target", ASCENDING)]),
        ]
