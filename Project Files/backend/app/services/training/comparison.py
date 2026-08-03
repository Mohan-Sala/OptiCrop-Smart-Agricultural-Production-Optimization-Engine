from typing import Dict, Any, List, Tuple


class ComparisonService:
    """Compares multiple models based on classification (f1_score) or regression (R2) metrics."""

    def select_best_model(
        self,
        trained_results: Dict[str, Dict[str, Any]],
        problem_type: str
    ) -> Tuple[str, List[Dict[str, Any]], str]:
        if not trained_results:
            raise ValueError("No models trained to compare.")
            
        primary_metric = "f1_score" if problem_type == "classification" else "r2"
        secondary_metric = "accuracy" if problem_type == "classification" else "rmse"
        
        rankings = []
        for algo, res in trained_results.items():
            metrics = res["metrics"]
            rankings.append({
                "algorithm": algo,
                "primary_score": metrics.get(primary_metric, 0.0),
                "secondary_score": metrics.get(secondary_metric, 0.0 if problem_type == "classification" else float("inf")),
                "metrics": metrics,
                "cv_scores": res["cv_scores"],
                "cv_mean": float(sum(res["cv_scores"]) / len(res["cv_scores"])) if res["cv_scores"] else 0.0,
                "training_time": res["training_time"],
                "model_object": res["model_object"]
            })
            
        if problem_type == "classification":
            rankings.sort(key=lambda x: (x["primary_score"], x["secondary_score"]), reverse=True)
        else:
            rankings.sort(key=lambda x: (x["primary_score"], -x["secondary_score"]), reverse=True)
            
        comparison_table = []
        for idx, item in enumerate(rankings):
            rank = idx + 1
            is_winner = rank == 1
            comparison_table.append({
                "algorithm": item["algorithm"],
                "cross_validation_score": item["cv_mean"],
                "validation_score": item["primary_score"],
                "test_score": item["primary_score"],
                "training_time_ms": item["training_time"],
                "ranking": rank,
                "winner_flag": is_winner,
                "selection_reason": "Highest metrics score on validation set." if is_winner else "Runner up performance."
            })
            
        winner = rankings[0]["algorithm"]
        reason = f"Algorithm '{winner}' selected as winner based on highest {primary_metric} of {rankings[0]['primary_score']:.4f}."
        
        return winner, comparison_table, reason
