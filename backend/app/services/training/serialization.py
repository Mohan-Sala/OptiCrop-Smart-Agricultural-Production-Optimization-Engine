import os
import joblib
import hashlib
from typing import Any, Tuple
from app.core.config import settings


class SerializationService:
    """Serializes scikit-learn model artifacts using joblib and calculates hashes."""

    def serialize_model(self, model: Any, model_id: Any) -> Tuple[str, str]:
        """Saves model to temporary local folder, calculates checksum.

        Returns:
            temp_path (str): Local file path.
            checksum (str): SHA-256 string.
        """
        os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
        temp_path = os.path.join(settings.UPLOAD_PATH, f"model_{model_id}.joblib")
        
        joblib.dump(model, temp_path)
        
        sha256 = hashlib.sha256()
        with open(temp_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        checksum = sha256.hexdigest()
        
        return temp_path, checksum

    def deserialize_model(self, file_path: str) -> Any:
        return joblib.load(file_path)
