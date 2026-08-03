from typing import List
from app.schemas.analytics import ChartDTO


class ConfusionMatrixBuilder:
    """Builds standardized ChartDTO for Confusion Matrices heatmap plotting."""

    def build(self, matrix: List[List[int]], labels: List[str]) -> ChartDTO:
        series_data = []
        for r_idx, row in enumerate(matrix):
            for c_idx, val in enumerate(row):
                series_data.append([c_idx, r_idx, int(val)])
                
        return ChartDTO(
            chart_type="heatmap",
            title="Confusion Matrix Heatmap",
            series=[
                {
                    "name": "Confusion Matrix Cells",
                    "data": series_data
                }
            ],
            axes={
                "x_categories": labels,
                "y_categories": labels
            },
            metadata={"matrix_raw": matrix}
        )
