from typing import List
from app.schemas.analytics import ChartDTO


class RocCurveBuilder:
    """Builds standardized ChartDTO for ROC curves plotting."""

    def build(self, fpr: List[float], tpr: List[float], auc: float) -> ChartDTO:
        return ChartDTO(
            chart_type="line",
            title=f"Receiver Operating Characteristic (AUC = {auc:.4f})",
            series=[
                {
                    "name": "ROC Curve",
                    "x": fpr,
                    "y": tpr,
                    "color": "#2563eb"
                },
                {
                    "name": "Random Baseline",
                    "x": [0.0, 1.0],
                    "y": [0.0, 1.0],
                    "dash": True,
                    "color": "#9ca3af"
                }
            ],
            axes={
                "x_axis_label": "False Positive Rate (FPR)",
                "y_axis_label": "True Positive Rate (TPR)"
            },
            metadata={"auc": auc}
        )
