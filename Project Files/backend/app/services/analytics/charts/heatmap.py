from typing import List
from app.schemas.analytics import ChartDTO


class HeatmapBuilder:
    """Builds standardized ChartDTO for correlation matrices plotting."""

    def build(self, matrix: List[List[float]], labels: List[str], title: str) -> ChartDTO:
        series_data = []
        for r_idx, row in enumerate(matrix):
            for c_idx, val in enumerate(row):
                series_data.append([c_idx, r_idx, float(val)])
                
        return ChartDTO(
            chart_type="heatmap",
            title=title,
            series=[
                {
                    "name": "Correlation Score",
                    "data": series_data
                }
            ],
            axes={
                "x_categories": labels,
                "y_categories": labels
            }
        )
