from typing import List
from app.schemas.analytics import ChartDTO


class ResidualPlotBuilder:
    """Builds standardized ChartDTO for residuals scatter plotting."""

    def build(self, actual: List[float], predicted: List[float]) -> ChartDTO:
        residuals = [act - pred for act, pred in zip(actual, predicted)]
        series_data = []
        for pred, res in zip(predicted, residuals):
            series_data.append({"x": float(pred), "y": float(res)})
            
        x_min = float(min(predicted)) if predicted else 0.0
        x_max = float(max(predicted)) if predicted else 100.0
        
        return ChartDTO(
            chart_type="scatter",
            title="Residuals Scatter Plot",
            series=[
                {
                    "name": "Residuals",
                    "data": series_data,
                    "color": "#ea580c"
                },
                {
                    "name": "Zero Error Line",
                    "x": [x_min, x_max],
                    "y": [0.0, 0.0],
                    "dash": True,
                    "color": "#9ca3af"
                }
            ],
            axes={
                "x_axis_label": "Predicted Values",
                "y_axis_label": "Residuals"
            }
        )
