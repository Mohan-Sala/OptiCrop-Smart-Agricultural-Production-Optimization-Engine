import pandas as pd
from typing import Dict, Tuple, Any
from app.utils.exceptions import ValidationException


class MissingValueService:
    """Applies numeric and categorical imputation strategies to datasets."""

    def impute(self, df: pd.DataFrame, target_column: str, strategy_config: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        df = df.copy()
        summary = {}
        
        numeric_strat = strategy_config.get("numeric_strategy", "median")
        categorical_strat = strategy_config.get("categorical_strategy", "most_frequent")
        overrides = strategy_config.get("columns_overrides", {})
        
        for col in df.columns:
            if col == target_column:
                continue
                
            null_count = int(df[col].isnull().sum())
            if null_count == 0:
                continue
                
            is_numeric = pd.api.types.is_numeric_dtype(df[col])
            col_strat = overrides.get(col, numeric_strat if is_numeric else categorical_strat)
            col_constant = overrides.get(f"{col}_constant", None)
            
            if col_strat == "drop_columns":
                df = df.drop(columns=[col])
                summary[col] = {"action": "drop_column", "null_count": null_count}
                continue
                
            elif col_strat == "drop_rows":
                df = df.dropna(subset=[col])
                summary[col] = {"action": "drop_rows", "null_count": null_count}
                continue
                
            elif col_strat == "mean":
                if not is_numeric:
                    raise ValidationException(f"Mean imputer cannot be applied to non-numeric column: {col}")
                fill_value = float(df[col].mean()) if not df[col].isnull().all() else 0.0
                
            elif col_strat == "median":
                if not is_numeric:
                    raise ValidationException(f"Median imputer cannot be applied to non-numeric column: {col}")
                fill_value = float(df[col].median()) if not df[col].isnull().all() else 0.0
                
            elif col_strat == "mode" or col_strat == "most_frequent":
                mode_series = df[col].mode()
                fill_value = mode_series[0] if not mode_series.empty else ("Unknown" if not is_numeric else 0.0)
                if is_numeric:
                    fill_value = float(fill_value)
                else:
                    fill_value = str(fill_value)
                    
            elif col_strat == "constant":
                fill_value = col_constant
                if fill_value is None:
                    fill_value = 0.0 if is_numeric else "Constant"
            else:
                raise ValidationException(f"Unknown imputer strategy: {col_strat} for column: {col}")
                
            df[col] = df[col].fillna(fill_value)
            summary[col] = {"action": f"impute_{col_strat}", "fill_value": fill_value, "null_count": null_count}
            
        return df, summary
