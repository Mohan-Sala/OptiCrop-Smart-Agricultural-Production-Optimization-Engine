from typing import List, Dict, Any
from app.schemas.analytics import ChartDTO


class ComparisonChartBuilder:
    """Builds standardized ChartDTO for models performance comparisons plotting."""

    def build(self, comparison_table: List[Dict[str, Any]], metric_name: str) -> ChartDTO:
        names = [item["algorithm"] for item in comparison_table]
        scores = [item["validation_score"] for item in comparison_table]
        times = [item["training_time_ms"] / 1000.0 for item in comparison_table]
        
        return ChartDTO(
            chart_type="bar",
            title=f"Model Performance Comparison ({metric_name})",
            series=[
                {
                    "name": "Validation Score",
                    "data": scores,
                    "color": "#10b981"
                },
                {
                    "name": "Training Duration (s)",
                    "data": times,
                    "color": "#f59e0b"
                }
            ],
            axes={
                "x_categories": names,
                "y_axis_label": "Value"
            }
        )
