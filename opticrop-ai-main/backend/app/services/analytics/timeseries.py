from datetime import datetime
from typing import Any, List, Dict


class TimeseriesService:
    """Aggregates history, growth, and timeline records over days, weeks, or months."""

    def group_by_day(self, items: List[Dict[str, Any]], date_key: str = "date") -> List[Dict[str, Any]]:
        buckets: Dict[str, float] = {}
        for item in items:
            date_val = item.get(date_key)
            if isinstance(date_val, str):
                dt = datetime.fromisoformat(date_val.replace("Z", "+00:00"))
            else:
                dt = date_val
                
            if not dt:
                continue
                
            day_str = dt.strftime("%Y-%m-%d")
            buckets[day_str] = buckets.get(day_str, 0.0) + float(item.get("value", 1.0))
            
        timeline = []
        for day in sorted(buckets.keys()):
            timeline.append({"date": day, "value": buckets[day]})
        return timeline
