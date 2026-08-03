from typing import Dict, Any, List
from app.utils.exceptions import ValidationException


class PredictionValidationService:
    """Validates features input lists against model signature columns and datatypes."""

    def validate_features(self, features: Dict[str, Any], signature: Dict[str, Any]) -> None:
        expected_names = signature.get("feature_names", [])
        expected_dtypes = signature.get("expected_dtypes", {})
        
        missing = [col for col in expected_names if col not in features]
        if missing:
            raise ValidationException(f"Missing required feature columns: {missing}")
            
        unexpected = [col for col in features if col not in expected_names]
        if unexpected:
            raise ValidationException(f"Unexpected columns in request: {unexpected}")
            
        for col, val in features.items():
            expected_type = expected_dtypes.get(col, "").lower()
            
            if "float" in expected_type or "double" in expected_type:
                if not isinstance(val, (int, float)):
                    raise ValidationException(f"Column '{col}' expects numeric type, got '{type(val).__name__}'")
            elif "int" in expected_type:
                if not isinstance(val, int) and not (isinstance(val, float) and val.is_integer()):
                    raise ValidationException(f"Column '{col}' expects integer type, got '{type(val).__name__}'")
            elif "bool" in expected_type:
                if not isinstance(val, bool):
                    raise ValidationException(f"Column '{col}' expects boolean type, got '{type(val).__name__}'")
            elif "str" in expected_type or "object" in expected_type:
                if not isinstance(val, (str, bytes)):
                    raise ValidationException(f"Column '{col}' expects string type, got '{type(val).__name__}'")
