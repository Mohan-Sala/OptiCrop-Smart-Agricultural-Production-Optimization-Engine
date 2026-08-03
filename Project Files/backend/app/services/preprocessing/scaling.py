import pandas as pd
from typing import Dict, Tuple, Any, List
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, Normalizer
from app.utils.exceptions import ValidationException


class ScalingService:
    """Scales and normalizes numerical features in the dataframe."""

    def scale(
        self, df: pd.DataFrame, target_column: str, scaling_mappings: Dict[str, str]
    ) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
        df = df.copy()
        fitted_scalers = {}
        lineage = {}
        
        for col, scaler_type in scaling_mappings.items():
            if col not in df.columns:
                continue
                
            if col == target_column:
                raise ValidationException(f"Target column '{col}' cannot be scaled.")
                
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValidationException(f"Scaling cannot be applied to non-numeric column: {col}")
                
            if scaler_type == "StandardScaler":
                scaler = StandardScaler()
            elif scaler_type == "MinMaxScaler":
                scaler = MinMaxScaler()
            elif scaler_type == "RobustScaler":
                scaler = RobustScaler()
            elif scaler_type == "Normalizer":
                scaler = Normalizer()
            else:
                raise ValidationException(f"Unsupported scaler type: {scaler_type} for column: {col}")
                
            scaled_arr = scaler.fit_transform(df[[col]])
            df[col] = scaled_arr.ravel()
            fitted_scalers[col] = scaler
            
            lineage[col] = [
                {
                    "original_column_name": col,
                    "transformed_column_name": col,
                    "transformation_type": scaler_type,
                    "preprocessing_step": "scaling"
                }
            ]
            
        return df, fitted_scalers, lineage
