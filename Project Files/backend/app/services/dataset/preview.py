import anyio
import pandas as pd
from typing import Dict, List, Any
import numpy as np


class PreviewService:
    """Uses Pandas to extract column statistics, null rates, data samples, and schemas."""

    async def generate_preview(self, file_path: str, delimiter: str = ",", encoding: str = "utf-8") -> Dict[str, Any]:
        """Reads the first 10 rows and gathers basic dimensions."""
        def _preview():
            # Get dimensions
            full_df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
            full_df_shape = list(full_df.shape)
            
            # Format rows as dict list, cleaning up NaN to None for JSON compatibility
            df_sample = full_df.head(10).replace({np.nan: None})
            data_sample = df_sample.to_dict(orient="records")
            
            columns = list(full_df.columns)
            dtypes = {col: str(full_df[col].dtype) for col in columns}
            
            # Calculate missing rates
            missing = full_df.isnull().sum().to_dict()
            missing = {k: int(v) for k, v in missing.items()}
            
            memory_bytes = int(full_df.memory_usage(deep=True).sum())
            
            return {
                "shape": full_df_shape,
                "columns": columns,
                "dtypes": dtypes,
                "missing_values": missing,
                "memory_usage_bytes": memory_bytes,
                "data": data_sample,
            }

        return await anyio.to_thread.run_sync(_preview)

    async def calculate_statistics(self, file_path: str, delimiter: str = ",", encoding: str = "utf-8") -> Dict[str, Any]:
        """Calculates detailed columns summaries and duplicates for the Statistics table."""
        def _stats():
            df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
            
            # Missing values summary
            missing = df.isnull().sum().to_dict()
            missing = {k: int(v) for k, v in missing.items()}
            
            # Duplicate rates
            dup_rows = int(df.duplicated().sum())
            dup_cols = 0
            
            memory_bytes = int(df.memory_usage(deep=True).sum())
            
            # Column descriptions
            summary = {}
            for col in df.columns:
                col_series = df[col]
                col_type = str(col_series.dtype)
                col_info = {"dtype": col_type}
                
                # Check for numerical properties
                if np.issubdtype(col_series.dtype, np.number):
                    col_info.update({
                        "min": float(col_series.min()) if not pd.isnull(col_series.min()) else None,
                        "max": float(col_series.max()) if not pd.isnull(col_series.max()) else None,
                        "mean": float(col_series.mean()) if not pd.isnull(col_series.mean()) else None,
                        "std": float(col_series.std()) if not pd.isnull(col_series.std()) else None,
                    })
                else:
                    col_info.update({
                        "unique_count": int(col_series.nunique()),
                        "top_value": str(col_series.mode()[0]) if not col_series.mode().empty else None,
                    })
                summary[col] = col_info

            return {
                "missing_values": missing,
                "duplicate_rows": dup_rows,
                "duplicate_columns": dup_cols,
                "memory_usage": memory_bytes,
                "column_summary": summary
            }

        return await anyio.to_thread.run_sync(_stats)
