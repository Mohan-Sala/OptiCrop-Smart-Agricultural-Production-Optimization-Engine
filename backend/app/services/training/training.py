import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.model_selection import KFold, StratifiedKFold, GridSearchCV
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, SVR
from sklearn.naive_bayes import GaussianNB

from app.utils.exceptions import ValidationException


class TrainingService:
    """Trains and executes hyperparameter search on multiple scikit-learn models."""

    def _get_estimator(self, algo_name: str, problem_type: str, seed: int) -> Any:
        name = algo_name.lower().replace(" ", "").replace("_", "")
        
        if problem_type == "classification":
            if name in ("logisticregression", "lr"):
                return LogisticRegression(random_state=seed, max_iter=1000)
            elif name in ("decisiontree", "decisiontreeclassifier"):
                return DecisionTreeClassifier(random_state=seed)
            elif name in ("randomforest", "randomforestclassifier"):
                return RandomForestClassifier(random_state=seed)
            elif name in ("knearestneighbors", "knn"):
                return KNeighborsClassifier()
            elif name in ("supportvectormachine", "svm", "svc"):
                return SVC(random_state=seed, probability=True)
            elif name in ("gaussiannaivebayes", "naivebayes", "gnb"):
                return GaussianNB()
            else:
                raise ValidationException(f"Unsupported classification algorithm: {algo_name}")
        elif problem_type == "regression":
            if name in ("linearregression", "lr"):
                return LinearRegression()
            elif name in ("decisiontree", "decisiontreeregressor"):
                return DecisionTreeRegressor(random_state=seed)
            elif name in ("randomforest", "randomforestregressor"):
                return RandomForestRegressor(random_state=seed)
            elif name in ("supportvectorregression", "svr"):
                return SVR()
            elif name in ("gradientboosting", "gradientboostingregressor"):
                return GradientBoostingRegressor(random_state=seed)
            else:
                raise ValidationException(f"Unsupported regression algorithm: {algo_name}")
        else:
            raise ValidationException(f"Unknown problem type: {problem_type}")

    def train_algorithm(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        algo_name: str,
        problem_type: str,
        param_grid: Dict[str, List[Any]],
        cv_strategy: Dict[str, Any],
        seed: int
    ) -> Tuple[Any, Dict[str, Any], List[float]]:
        estimator = self._get_estimator(algo_name, problem_type, seed)
        
        cv_method = cv_strategy.get("method", "KFold")
        folds = int(cv_strategy.get("folds", 5))
        
        if cv_method == "StratifiedKFold" and problem_type == "classification":
            cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
        else:
            cv = KFold(n_splits=folds, shuffle=True, random_state=seed)
            
        if param_grid:
            grid_size = 1
            for vals in param_grid.values():
                grid_size *= len(vals)
            if grid_size > 20:
                truncated_grid = {}
                for k, vals in param_grid.items():
                    truncated_grid[k] = vals[:2]
                param_grid = truncated_grid
                
        scoring = "accuracy" if problem_type == "classification" else "r2"
        
        grid_search = GridSearchCV(
            estimator=estimator,
            param_grid=param_grid or {},
            cv=cv,
            scoring=scoring,
            n_jobs=1,
            refit=True
        )
        grid_search.fit(X_train, y_train)
        
        best_estimator = grid_search.best_estimator_
        best_params = grid_search.best_params_
        
        cv_results = grid_search.cv_results_
        best_index = grid_search.best_index_
        fold_scores = []
        for f in range(folds):
            score_key = f"split{f}_test_score"
            if score_key in cv_results:
                fold_scores.append(float(cv_results[score_key][best_index]))
                
        return best_estimator, best_params, fold_scores
