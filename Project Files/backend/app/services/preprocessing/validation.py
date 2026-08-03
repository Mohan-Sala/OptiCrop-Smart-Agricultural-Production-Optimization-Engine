import pandas as pd
from app.utils.exceptions import ValidationException


class PreprocessingValidationService:
    """Verifies dataset state and trainability thresholds before finalizing runs."""

    def validate_before_preprocessing(self, df: pd.DataFrame, target_column: str) -> None:
        """Checks target column presence and parameters validation."""
        if target_column not in df.columns:
            raise ValidationException(f"Target column '{target_column}' is missing from the dataset.")

    def validate_after_preprocessing(self, df: pd.DataFrame, target_column: str) -> None:
        """Enforces checks verifying the matrix is ready for model training without nulls or string types."""
        target_nulls = int(df[target_column].isnull().sum())
        if target_nulls > 0:
            raise ValidationException(
                f"Target column '{target_column}' contains {target_nulls} missing values. "
                f"Missing values on target column must be imputed or rows dropped."
            )
            
        feature_cols = [col for col in df.columns if col != target_column and not col.endswith("_outlier")]
        if len(feature_cols) < 1:
            raise ValidationException("Improper configuration: zero feature columns remaining after processing.")
            
        for col in feature_cols:
            null_count = int(df[col].isnull().sum())
            if null_count > 0:
                raise ValidationException(
                    f"Trainability check failed: Column '{col}' contains {null_count} unresolved missing values. "
                    f"All feature nulls must be processed before training."
                )
                
            if not pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col]):
                raise ValidationException(
                    f"Trainability check failed: Column '{col}' has type '{df[col].dtype}' which is non-numeric. "
                    f"All text categorical columns must be encoded."
                )
