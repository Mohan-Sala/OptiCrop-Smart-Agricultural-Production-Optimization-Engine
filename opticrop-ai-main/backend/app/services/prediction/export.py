import csv
import json
import io
from typing import List, Dict, Any


class PredictionExportService:
    """Serializes historical prediction run results to JSON and CSV formats."""

    def to_json(self, runs: List[Dict[str, Any]]) -> str:
        return json.dumps(runs, indent=2, default=str)

    def to_csv(self, runs: List[Dict[str, Any]]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            "prediction_id", "project_id", "model_id", "model_version",
            "prediction_count", "execution_time", "status", "timestamp"
        ])
        for run in runs:
            writer.writerow([
                run.get("id"),
                run.get("project_id"),
                run.get("model_id"),
                run.get("model_version"),
                run.get("prediction_count"),
                run.get("execution_time"),
                run.get("status"),
                run.get("prediction_timestamp"),
            ])
            
        return output.getvalue()
