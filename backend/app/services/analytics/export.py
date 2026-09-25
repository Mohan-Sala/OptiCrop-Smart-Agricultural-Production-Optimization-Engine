import csv
import json
import io
from typing import Dict, Any


class ExportService:
    """Serializes project aggregates and timeline reports into CSV and JSON export formats."""

    def to_json(self, data: Dict[str, Any]) -> str:
        return json.dumps(data, indent=2, default=str)

    def to_csv(self, metrics: Dict[str, Any]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["Metric Name", "Metric Value"])
        for key, val in metrics.items():
            writer.writerow([key, str(val)])
            
        return output.getvalue()
