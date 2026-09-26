import hashlib
import io
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
        content = await self.storage_service.download_file(storage_path)

        # Verify SHA-256 checksum if provided and not placeholder
        if expected_checksum and expected_checksum != "no_checksum":
            checksum = hashlib.sha256(content).hexdigest()
            if checksum != expected_checksum:
                logger.error(
                    "Integrity verification failed for path %s. Expected: %s, Computed: %s",
                    storage_path, expected_checksum, checksum
                )
                raise ValidationException("Artifact checksum mismatch: potential corruption detected.")

        # Try in-memory deserialization directly to avoid file system dependencies
        try:
            return joblib.load(io.BytesIO(content))
        except Exception as in_mem_err:
            logger.warning("In-memory joblib.load failed (%s), attempting filesystem fallback...", in_mem_err)
            os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
            temp_name = f"verify_{uuid.uuid4().hex}.joblib"
            temp_path = os.path.join(settings.UPLOAD_PATH, temp_name)

            try:
                with open(temp_path, "wb") as f:
                    f.write(content)
                loaded_obj = joblib.load(temp_path)
                return loaded_obj
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass

