import time
import pandas as pd
from typing import Dict, Any, List


class PreprocessingReportService:
    """Compiles timing checkpoints, transformation lineage, and stats drift baseline profiles."""

    def compile_report(
        self,
        df_raw: pd.DataFrame,
        df_processed: pd.DataFrame,
        target_column: str,
        missing_summary: Dict[str, Any],
        outlier_summary: Dict[str, Any],
        lineage_map: List[Dict[str, Any]],
        checkpoints: Dict[str, float],
        total_time_ms: float
    ) -> Dict[str, Any]:
        raw_dups = int(df_raw.duplicated().sum())
        processed_dups = int(df_processed.duplicated().sum())
        
        encoding_summary = [item for item in lineage_map if "Encoder" in item["transformation_type"]]
        scaling_summary = [item for item in lineage_map if "Scaler" in item["transformation_type"] or "Normalizer" in item["transformation_type"]]
        
        baseline = {}
        for col in df_processed.columns:
            series = df_processed[col]
            col_info = {"dtype": str(series.dtype)}
            
            if pd.api.types.is_numeric_dtype(series):
                col_info.update({
                    "mean": float(series.mean()) if not pd.isnull(series.mean()) else 0.0,
                    "std": float(series.std()) if not pd.isnull(series.std()) else 0.0,
                    "min": float(series.min()) if not pd.isnull(series.min()) else 0.0,
                    "max": float(series.max()) if not pd.isnull(series.max()) else 0.0,
                })
            baseline[col] = col_info
            
        feature_summary = []
        for col in df_processed.columns:
            is_target = col == target_column
            feature_summary.append({
                "feature_name": col,
                "feature_type": "TARGET" if is_target else "NUMERIC",
                "nullable": bool(df_processed[col].isnull().any()),
                "encoded": any(item["transformed_column_name"] == col and "Encoder" in item["transformation_type"] for item in lineage_map),
                "scaled": any(item["transformed_column_name"] == col and ("Scaler" in item["transformation_type"] or "Normalizer" in item["transformation_type"]) for item in lineage_map),
                "generated": col.endswith("_outlier"),
                "target": is_target
            })
            
        return {
            "processing_time_ms": total_time_ms,
            "checkpoints": checkpoints,
            "missing_value_summary": missing_summary,
            "duplicate_summary": {
                "raw_duplicate_rows": raw_dups,
                "processed_duplicate_rows": processed_dups,
                "removed_duplicate_rows": max(0, raw_dups - processed_dups)
            },
            "outlier_summary": outlier_summary,
            "encoding_summary": encoding_summary,
            "scaling_summary": scaling_summary,
            "column_lineage": lineage_map,
            "baseline_profile": baseline,
            "feature_summary": feature_summary
        }
