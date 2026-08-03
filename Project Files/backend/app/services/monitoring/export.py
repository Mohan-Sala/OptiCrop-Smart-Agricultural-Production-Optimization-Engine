import csv
import json
import io
from typing import List, Dict, Any


class MonitoringExportService:
    """Exports metrics logs, latency distributions, and active alert rules to JSON/CSV files."""

    def to_json(self, data: Any) -> str:
        return json.dumps(data, indent=2, default=str)

    def to_csv(self, alerts: List[Dict[str, Any]]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "alert_id", "rule_name", "severity", "message", "metric_value", "threshold_value", "status"
        ])
        for a in alerts:
            writer.writerow([
                a.get("id"),
                a.get("rule_name"),
                a.get("severity"),
                a.get("message"),
                a.get("metric_value"),
                a.get("threshold_value"),
                a.get("status"),
            ])
        return output.getvalue()
