import numpy as np
from typing import Any, List, Optional, Tuple


class InferenceService:
    """Invokes scikit-learn model predict and predict_proba calculations."""

    def predict(self, model: Any, X: np.ndarray) -> Tuple[List[Any], Optional[List[float]]]:
        predictions = model.predict(X)
        pred_list = predictions.tolist()
        
        confidence_scores = None
        if hasattr(model, "predict_proba"):
            try:
                probs = model.predict_proba(X)
                confidence_scores = np.max(probs, axis=1).tolist()
            except Exception:
                pass
                
        return pred_list, confidence_scores
