import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from app.models.dataset import Dataset
from app.models.dataset_preprocessing import DatasetPreprocessing
from app.models.preprocessing_artifact import PreprocessingArtifact
from app.utils.exceptions import ValidationException


class PredictionPreprocessingService:
    """Applies fitted scikit-learn transformers and imputation strategies to prediction dataframes."""

    def impute_missing(
        self,
        df: pd.DataFrame,
        dataset: Dataset,
        prep_run: Optional[DatasetPreprocessing]
    ) -> pd.DataFrame:
        df = df.copy()
        if not prep_run:
            return df
            
        config = prep_run.parameters or {}
        missing_config = config.get("missing_value_strategies", {})
        
        numeric_strat = missing_config.get("numeric_strategy", "median")
        categorical_strat = missing_config.get("categorical_strategy", "most_frequent")
        overrides = missing_config.get("columns_overrides", {})
        
        stats = dataset.statistics
        col_summary = stats.column_summary if stats else {}

        for col in df.columns:
            if df[col].isnull().any() or df[col].isna().any():
                is_numeric = col_summary.get(col, {}).get("type", "numeric") != "categorical"
                col_strat = overrides.get(col, numeric_strat if is_numeric else categorical_strat)
                col_constant = overrides.get(f"{col}_constant", None)
                
                if col_strat == "constant":
                    fill_value = col_constant if col_constant is not None else (0.0 if is_numeric else "Constant")
                elif col_strat == "mean":
                    fill_value = col_summary.get(col, {}).get("mean", 0.0)
                elif col_strat == "median":
                    fill_value = col_summary.get(col, {}).get("median", 0.0)
                elif col_strat in ["mode", "most_frequent"]:
                    fill_value = col_summary.get(col, {}).get("mode", "Unknown")
                else:
                    fill_value = 0.0 if is_numeric else "Unknown"
                    
                df[col] = df[col].fillna(fill_value)
        return df

    def transform_features(
        self,
        df: pd.DataFrame,
        prep_run: Optional[DatasetPreprocessing],
        loaded_transformers: Dict[str, Any]
    ) -> pd.DataFrame:
        """Applies loaded encoding and scaling transformers to prediction dataframes."""
        df = df.copy()
        if not prep_run:
            return df

        config = prep_run.parameters or {}
        
        encoding_mappings = config.get("encoding_mappings", {})
        for col, encoder_type in encoding_mappings.items():
            if col not in df.columns:
                continue
                
            transformer_key = f"{col}_{encoder_type}"
            if transformer_key not in loaded_transformers:
                continue
                
            transformer = loaded_transformers[transformer_key]
            
            if encoder_type == "OrdinalEncoder":
                encoded_arr = transformer.transform(df[[col]].astype(str))
                df[col] = encoded_arr.ravel()
            elif encoder_type == "OneHotEncoder":
                ohe_df = pd.DataFrame(
                    transformer.transform(df[[col]].astype(str)),
                    columns=[f"{col}_{cat}" for cat in transformer.categories_[0]],
                    index=df.index
                )
                df = df.drop(columns=[col])
                df = pd.concat([df, ohe_df], axis=1)

        scaling_mappings = config.get("scaling_mappings", {})
        for col, scaler_type in scaling_mappings.items():
            if col not in df.columns:
                continue
                
            transformer_key = f"{col}_{scaler_type}"
            if transformer_key not in loaded_transformers:
                continue
                
            transformer = loaded_transformers[transformer_key]
            scaled_arr = transformer.transform(df[[col]])
            df[col] = scaled_arr.ravel()

        return df
