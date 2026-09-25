from typing import Dict
from app.schemas.analytics import ChartDTO


class FeatureImportanceBuilder:
    """Builds standardized ChartDTO for feature importances bar plotting."""

    def build(self, importances: Dict[str, float]) -> ChartDTO:
        sorted_feats = sorted(importances.items(), key=lambda x: x[1], reverse=True)
        names = [item[0] for item in sorted_feats]
        values = [item[1] for item in sorted_feats]
        
        return ChartDTO(
            chart_type="bar",
            title="Feature Importances (Ranked)",
            series=[
                {
                    "name": "Importance Score",
                    "data": values,
                    "color": "#6366f1"
                }
            ],
            axes={
                "x_categories": names,
                "y_axis_label": "Score Coefficient"
            }
        )
