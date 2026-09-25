import pandas as pd
from typing import Dict, Tuple, Any, List
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder
from app.utils.exceptions import ValidationException


class EncodingService:
    """Transforms categorical text features into numeric formats."""

    def encode(
        self, df: pd.DataFrame, target_column: str, encoding_mappings: Dict[str, str]
    ) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
        """Fits encoders and transforms target categorical features in the dataframe.

        Returns:
            df (DataFrame): Modified dataframe.
            fitted_encoders (dict): Maps column name -> fitted scikit-learn encoder object.
            lineage (dict): Maps column name -> transformation mappings metadata list.
        """
        df = df.copy()
        fitted_encoders = {}
        lineage = {}
        
        for col, encoder_type in encoding_mappings.items():
            if col not in df.columns:
                continue
                
            if col == target_column:
                if encoder_type != "LabelEncoder":
                    raise ValidationException(f"Only LabelEncoder strategy is supported on target column: {col}")
                    
            unique_count = df[col].nunique()
            if encoder_type == "OneHotEncoder" and unique_count > 100:
                raise ValidationException(
                    f"Column '{col}' has {unique_count} unique categories. OneHotEncoder is rejected "
                    f"above 100 to prevent high dimensionality and memory crashes."
                )
                
            col_series = df[col].astype(str)
            
            if encoder_type == "LabelEncoder":
                le = LabelEncoder()
                df[col] = le.fit_transform(col_series)
                fitted_encoders[col] = le
                
                lineage[col] = [
                    {
                        "original_column_name": col,
                        "transformed_column_name": col,
                        "transformation_type": "LabelEncoder",
                        "preprocessing_step": "encoding"
                    }
                ]
                
            elif encoder_type == "OrdinalEncoder":
                oe = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
                encoded_arr = oe.fit_transform(df[[col]].astype(str))
                df[col] = encoded_arr.ravel()
                fitted_encoders[col] = oe
                
                lineage[col] = [
                    {
                        "original_column_name": col,
                        "transformed_column_name": col,
                        "transformation_type": "OrdinalEncoder",
                        "preprocessing_step": "encoding"
                    }
                ]
                
            elif encoder_type == "OneHotEncoder":
                ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
                ohe_df = pd.DataFrame(
                    ohe.fit_transform(df[[col]].astype(str)),
                    columns=[f"{col}_{cat}" for cat in ohe.categories_[0]],
                    index=df.index
                )
                
                lineage[col] = []
                for ohe_col in ohe_df.columns:
                    lineage[col].append({
                        "original_column_name": col,
                        "transformed_column_name": ohe_col,
                        "transformation_type": "OneHotEncoder",
                        "preprocessing_step": "encoding"
                    })
                    
                df = df.drop(columns=[col])
                df = pd.concat([df, ohe_df], axis=1)
                fitted_encoders[col] = ohe
                
            else:
                raise ValidationException(f"Unsupported encoder type: {encoder_type} for column: {col}")
                
        return df, fitted_encoders, lineage
