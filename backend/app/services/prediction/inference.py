import numpy as np
from typing import Any, List, Optional, Tuple, Dict


class InferenceService:
    """Invokes scikit-learn model predict and predict_proba calculations."""

    def predict(
        self, model: Any, X: np.ndarray
    ) -> Tuple[List[Any], Optional[List[float]], Optional[List[Dict[str, float]]]]:
        predictions = model.predict(X)
        pred_list = predictions.tolist()
        
        confidence_scores = None
        probabilities_list = None
        if hasattr(model, "predict_proba"):
            try:
                probs = model.predict_proba(X)
                confidence_scores = np.max(probs, axis=1).tolist()

                classes = getattr(model, "classes_", None)
                if classes is not None:
                    class_labels = [str(c) for c in classes]
                    probabilities_list = []
                    for row in probs:
                        row_dict = {
                            class_labels[i]: round(float(row[i]), 4)
                            for i in range(len(class_labels))
                        }
                        probabilities_list.append(row_dict)
            except Exception:
                pass
                
        return pred_list, confidence_scores, probabilities_list

