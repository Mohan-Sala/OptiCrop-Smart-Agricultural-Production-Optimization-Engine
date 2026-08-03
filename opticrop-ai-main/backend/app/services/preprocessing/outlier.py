import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any


class OutlierService:
    """Detects outliers using IQR bounds and Z-Score deviations."""

    def process_outliers(
        self, df: pd.DataFrame, target_column: str, strategy: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        df = df.copy()
        summary = {}
        
        method = strategy.get("method", "IQR")
        action = strategy.get("action", "flag_only")
        threshold = float(strategy.get("threshold", 3.0))
        
        for col in df.columns:
            if col == target_column or col.endswith("_outlier"):
                continue
                
            if not pd.api.types.is_numeric_dtype(df[col]):
                continue
                
            col_series = df[col]
            if col_series.nunique() <= 1:
                continue
                
            if method == "Z-Score":
                mean = col_series.mean()
                std = col_series.std()
                if pd.isnull(std) or std == 0:
                    continue
                z_scores = np.abs((col_series - mean) / std)
                outlier_mask = z_scores > threshold
            else:  # IQR
                Q1 = col_series.quantile(0.25)
                Q3 = col_series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_mask = (col_series < lower_bound) | (col_series > upper_bound)
                
            outlier_count = int(outlier_mask.sum())
            if outlier_count == 0:
                continue
                
            if action == "remove":
                df = df[~outlier_mask]
                summary[col] = {
                    "method": method,
                    "action": "remove",
                    "outlier_count": outlier_count
                }
            else:
                df[f"{col}_outlier"] = outlier_mask.astype(int)
                summary[col] = {
                    "method": method,
                    "action": "flag_only",
                    "outlier_count": outlier_count
                }
                
        return df, summary
