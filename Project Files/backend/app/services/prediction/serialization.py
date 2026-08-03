import hashlib
import os
import uuid
import logging
import joblib
from typing import Any
from app.core.config import settings
from app.services.dataset.storage import StorageService
from app.utils.exceptions import ValidationException

logger = logging.getLogger("app.services.prediction.serialization")


class PredictionSerializationService:
    """Safely downloads and validates SHA-256 integrity checksums before joblib.load execution."""

    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service

    async def download_and_verify(self, storage_path: str, expected_checksum: str) -> Any:
        temp_name = f"verify_{uuid.uuid4().hex}.joblib"
        temp_path = os.path.join(settings.UPLOAD_PATH, temp_name)
        
        try:
            content = await self.storage_service.download_file(storage_path)
            with open(temp_path, "wb") as f:
                f.write(content)
                
            sha256 = hashlib.sha256()
            with open(temp_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            checksum = sha256.hexdigest()
            
            if checksum != expected_checksum:
                logger.error(
                    "Integrity verification failed for path %s. Expected: %s, Computed: %s",
                    storage_path, expected_checksum, checksum
                )
                raise ValidationException("Artifact checksum mismatch: potential corruption detected.")
                
            loaded_obj = joblib.load(temp_path)
            return loaded_obj
            
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
