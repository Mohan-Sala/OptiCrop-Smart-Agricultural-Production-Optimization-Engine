from typing import List
from app.schemas.analytics import ChartDTO


class PrCurveBuilder:
    """Builds standardized ChartDTO for Precision-Recall curves plotting."""

    def build(self, precision: List[float], recall: List[float]) -> ChartDTO:
        return ChartDTO(
            chart_type="line",
            title="Precision-Recall Curve",
            series=[
                {
                    "name": "PR Curve",
                    "x": recall,
                    "y": precision,
                    "color": "#16a34a"
                }
            ],
            axes={
                "x_axis_label": "Recall",
                "y_axis_label": "Precision"
            }
        )
