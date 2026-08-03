from typing import List, Dict, Any
from app.schemas.analytics import ChartDTO


class TimelineChartBuilder:
    """Builds standardized ChartDTO for time-series timelines plotting."""

    def build(self, timeline_data: List[Dict[str, Any]], title: str) -> ChartDTO:
        dates = [item["date"] for item in timeline_data]
        values = [item["value"] for item in timeline_data]
        
        return ChartDTO(
            chart_type="line",
            title=title,
            series=[
                {
                    "name": "Activity count",
                    "data": values,
                    "color": "#a855f7"
                }
            ],
            axes={
                "x_categories": dates,
                "y_axis_label": "Occurrences"
            }
        )
