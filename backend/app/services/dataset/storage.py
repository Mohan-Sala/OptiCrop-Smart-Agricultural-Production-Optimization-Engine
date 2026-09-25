from typing import Optional
from app.storage.gridfs import GridFSStorageService
from app.core.config import settings


class StorageService(GridFSStorageService):
    """MongoDB GridFS Object Storage service."""

    def __init__(self, bucket_name: Optional[str] = None):
        target_bucket = bucket_name or settings.GRIDFS_DATASETS_BUCKET or "datasets"
        super().__init__(bucket_name=target_bucket)
