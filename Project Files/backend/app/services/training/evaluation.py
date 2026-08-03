import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, roc_auc_score, roc_curve, precision_recall_curve, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score, explained_variance_score
)


class EvaluationService:
    """Evaluates scikit-learn models, computing classifications, regressions, and feature importance matrices."""

    def evaluate_model(
        self,
        model: Any,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        problem_type: str
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        metrics = {}
        report_visualizations = {}
        
        y_pred = model.predict(X_test)
        
        if problem_type == "classification":
            metrics["accuracy"] = float(accuracy_score(y_test, y_pred))
            prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)
            metrics["precision"] = float(prec)
            metrics["recall"] = float(rec)
            metrics["f1_score"] = float(f1)
            
            if hasattr(model, "predict_proba"):
                try:
                    y_prob = model.predict_proba(X_test)
                    if len(model.classes_) == 2:
                        y_prob_positive = y_prob[:, 1]
                        auc = roc_auc_score(y_test, y_prob_positive)
                        metrics["roc_auc"] = float(auc)
                        
                        fpr, tpr, _ = roc_curve(y_test, y_prob_positive)
                        precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_prob_positive)
                        
                        report_visualizations["roc_curve"] = {
                            "fpr": fpr.tolist(),
                            "tpr": tpr.tolist()
                        }
                        report_visualizations["precision_recall_curve"] = {
                            "precision": precision_curve.tolist(),
                            "recall": recall_curve.tolist()
                        }
                    else:
                        auc = roc_auc_score(y_test, y_prob, multi_class="ovr", average="weighted")
                        metrics["roc_auc"] = float(auc)
                except Exception:
                    metrics["roc_auc"] = 0.0
            else:
                metrics["roc_auc"] = 0.0
                
            cm = confusion_matrix(y_test, y_pred)
            report_visualizations["confusion_matrix"] = cm.tolist()
            report_visualizations["prediction_vs_actual"] = {
                "actual": y_test.tolist(),
                "predicted": y_pred.tolist()
            }
            
        else:  # Regression
            metrics["mae"] = float(mean_absolute_error(y_test, y_pred))
            mse = mean_squared_error(y_test, y_pred)
            metrics["mse"] = float(mse)
            metrics["rmse"] = float(np.sqrt(mse))
            metrics["r2"] = float(r2_score(y_test, y_pred))
            metrics["explained_variance"] = float(explained_variance_score(y_test, y_pred))
            
            residuals = y_test - y_pred
            report_visualizations["residuals"] = residuals.tolist()
            report_visualizations["prediction_vs_actual"] = {
                "actual": y_test.tolist(),
                "predicted": y_pred.tolist()
            }
            
        feature_importance = {}
        feature_names = X_test.columns.tolist()
        
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            for col, imp in zip(feature_names, importances):
                feature_importance[col] = float(imp)
        elif hasattr(model, "coef_"):
            coefs = model.coef_
            if coefs.ndim > 1:
                coefs = coefs[0]
            for col, coef in zip(feature_names, coefs):
                feature_importance[col] = float(coef)
                
        report_visualizations["feature_importance"] = feature_importance
        
        return metrics, report_visualizations
