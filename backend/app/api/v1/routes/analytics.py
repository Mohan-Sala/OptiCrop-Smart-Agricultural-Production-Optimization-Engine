import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import get_active_user
from app.dependencies.dataset import get_project_repository, get_dataset_repository
from app.dependencies.training import get_trained_model_repository
from app.dependencies.analytics import (
    get_project_analytics_repository,
    get_dataset_analytics_repository,
    get_training_analytics_repository,
    get_model_analytics_repository,
    get_comparison_analytics_repository,
    get_analytics_cache,
    get_statistics_service,
    get_timeseries_service,
    get_lineage_graph_service,
    get_export_service,
    get_aggregation_service,
    get_dataset_dashboard_service,
    get_training_dashboard_service,
    get_model_dashboard_service,
    get_activity_dashboard_service,
)
from app.schemas.analytics import (
    HealthResponse,
    DashboardResponse,
    ChartDTO,
    ComparisonDTO,
    LineageDTO,
    ExportResponse,
)
from app.utils.exceptions import NotFoundException, ValidationException
from app.services.analytics.charts.roc import RocCurveBuilder
from app.services.analytics.charts.pr_curve import PrCurveBuilder
from app.services.analytics.charts.confusion_matrix import ConfusionMatrixBuilder
from app.services.analytics.charts.residual import ResidualPlotBuilder
from app.services.analytics.charts.feature_importance import FeatureImportanceBuilder
from app.services.analytics.charts.comparison import ComparisonChartBuilder

router = APIRouter()


# --- 1. HEALTH MONITORING ---

@router.get("/health", response_model=HealthResponse)
async def check_analytics_health(
    current_user=Depends(get_active_user),
    cache=Depends(get_analytics_cache),
):
    """Analytics dashboard health checkpoint."""
    # Ensure cache is functional
    cache.set("health_check_key", "ok", ttl=5)
    cache_status = "healthy" if cache.get("health_check_key") == "ok" else "degraded"
    
    return HealthResponse(
        cache=cache_status,
        database="healthy",
        aggregation="healthy",
    )


# --- 2. OVERVIEW DASHBOARD ---

@router.get("/project/{project_id}/overview", response_model=DashboardResponse)
async def get_project_overview(
    project_id: uuid.UUID,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    cache=Depends(get_analytics_cache),
    agg_service=Depends(get_aggregation_service),
    activity_service=Depends(get_activity_dashboard_service),
):
    """Aggregates overview metrics, counts, and recent activity logs under the project workspace."""
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found or access denied.")

    cache_key = f"project_overview:{project_id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        # Re-fetch recent activities dynamically to ensure freshness
        activities = await activity_service.get_recent_activity(project_id)
        cached_data["recent_activity"] = activities
        return DashboardResponse(**cached_data)

    summary = await agg_service.aggregate_project_summary(project_id)
    activities = await activity_service.get_recent_activity(project_id)
    summary["recent_activity"] = activities

    cache.set(cache_key, summary, ttl=600)
    return DashboardResponse(**summary)


# --- 3. DATASET LINEAGE GRAPH ---

@router.get("/project/{project_id}/lineage", response_model=LineageDTO)
async def get_project_lineage_dag(
    project_id: uuid.UUID,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    dataset_repo=Depends(get_dataset_repository),
    cache=Depends(get_analytics_cache),
    graph_service=Depends(get_lineage_graph_service),
):
    """Compiles recursive parent-link relationship DAG showing stages distribution."""
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found or access denied.")

    cache_key = f"lineage:{project_id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return LineageDTO(**cached_data)

    datasets = await dataset_repo.get_by_project_id(project_id)
    dag = graph_service.build_lineage_dag(datasets)
    dag["project_id"] = project_id

    cache.set(cache_key, dag, ttl=600)
    return LineageDTO(**dag)


# --- 4. MODEL COMPARISONS ---

@router.get("/project/{project_id}/compare", response_model=ComparisonDTO)
async def compare_models_metrics(
    project_id: uuid.UUID,
    model_ids: str = Query(..., description="Comma-separated UUIDs of models to compare"),
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    cache=Depends(get_analytics_cache),
    compare_repo=Depends(get_comparison_analytics_repository),
):
    """Compares metrics, hyperparameter configurations, and performance deltas across a list of models."""
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found or access denied.")

    try:
        uuids = [uuid.UUID(uid.strip()) for uid in model_ids.split(",") if uid.strip()]
    except ValueError:
        raise ValidationException("Invalid UUID list format.")

    if not uuids:
        raise ValidationException("Model IDs list cannot be empty.")

    sorted_ids_str = ",".join(sorted(str(uid) for uid in uuids))
    cache_key = f"model_compare:{sorted_ids_str}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return ComparisonDTO(**cached_data)

    models = await compare_repo.get_models_by_ids(uuids)
    if len(models) != len(uuids):
        raise NotFoundException("Some requested models were not found.")

    # Ensure all models belong to this project
    for m in models:
        if m.training_session.dataset.project_id != project_id:
            raise ValidationException(f"Model {m.id} does not belong to this project.")

    comparison_table = []
    hyperparams_comparison = {}
    
    # Track the active validation score for delta computations (relative to first model in list)
    baseline_metrics = {}
    metrics_deltas = {}

    for idx, m in enumerate(models):
        metrics_dict = {met.metric_name: met.metric_value for met in m.metrics}
        
        # Pull validation score
        val_score = metrics_dict.get("accuracy", metrics_dict.get("r2", 0.0))
        
        comparison_table.append({
            "model_id": str(m.id),
            "model_name": m.model_name,
            "algorithm": m.algorithm,
            "validation_score": val_score,
            "training_time_ms": m.training_session.training_time * 1000 if m.training_session.training_time else 0.0,
            "version": m.version,
            "is_active": m.is_active,
        })
        
        hyperparams_comparison[str(m.id)] = m.hyperparameters or {}

        # Compute differences against baseline
        if idx == 0:
            baseline_metrics = metrics_dict
            metrics_deltas[str(m.id)] = {k: 0.0 for k in metrics_dict.keys()}
        else:
            deltas = {}
            for k, val in metrics_dict.items():
                base_val = baseline_metrics.get(k, 0.0)
                deltas[k] = round(val - base_val, 4)
            metrics_deltas[str(m.id)] = deltas

    result = {
        "project_id": project_id,
        "comparison_table": comparison_table,
        "metrics_deltas": metrics_deltas,
        "hyperparameters_comparison": hyperparams_comparison,
    }

    cache.set(cache_key, result, ttl=600)
    return ComparisonDTO(**result)


# --- 5. EVALUATION CURVES & FEATURE IMPORTANCE ---

@router.get("/models/{model_id}/plots", response_model=List[ChartDTO])
async def get_model_plots(
    model_id: uuid.UUID,
    current_user=Depends(get_active_user),
    model_repo=Depends(get_trained_model_repository),
):
    """Extracts pre-computed evaluation reports to format ROC, PR, Confusion matrix, and Residuals charts."""
    model = await model_repo.get_by_id(model_id)
    if not model:
        raise NotFoundException("Model not found or access denied.")

    # Eager verify project/dataset owner
    if model.training_session.dataset.user_id != current_user.id:
        raise NotFoundException("Access denied.")

    report = model.evaluation_report
    if not report or not report.report_data:
        return []

    winner_visuals = report.report_data.get("winner_visuals", {})
    charts = []

    # Compile ROC Curve
    if "fpr" in winner_visuals and "tpr" in winner_visuals:
        auc_val = report.report_data.get("winner_metrics", {}).get("roc_auc", 1.0)
        charts.append(
            RocCurveBuilder().build(winner_visuals["fpr"], winner_visuals["tpr"], auc_val)
        )

    # Compile PR Curve
    if "precision" in winner_visuals and "recall" in winner_visuals:
        charts.append(
            PrCurveBuilder().build(winner_visuals["precision"], winner_visuals["recall"])
        )

    # Compile Confusion Matrix Heatmap
    if "confusion_matrix" in winner_visuals:
        matrix = winner_visuals["confusion_matrix"]
        charts.append(
            ConfusionMatrixBuilder().build(matrix, ["Class 0", "Class 1"])
        )

    # Compile Residuals Plot (for regression)
    if "actual" in winner_visuals and "predicted" in winner_visuals:
        charts.append(
            ResidualPlotBuilder().build(winner_visuals["actual"], winner_visuals["predicted"])
        )

    return charts


@router.get("/models/{model_id}/features", response_model=ChartDTO)
async def get_model_features_importance(
    model_id: uuid.UUID,
    current_user=Depends(get_active_user),
    model_repo=Depends(get_trained_model_repository),
):
    """Exposes feature importance bar chart coefficients."""
    model = await model_repo.get_by_id(model_id)
    if not model:
        raise NotFoundException("Model not found or access denied.")

    if model.training_session.dataset.user_id != current_user.id:
        raise NotFoundException("Access denied.")

    report = model.evaluation_report
    if not report or not report.report_data:
        raise NotFoundException("Report data unavailable.")

    winner_visuals = report.report_data.get("winner_visuals", {})
    importances = winner_visuals.get("feature_importances", {})
    
    # Handlers for linear models lacking native trees tree_importances or coefficients
    if not importances:
        importances = {"No Importances Available": 0.0}

    return FeatureImportanceBuilder().build(importances)


# --- 6. DATASET EXPORTS ---

@router.get("/project/{project_id}/export/{export_format}", response_model=ExportResponse)
async def export_project_aggregates(
    project_id: uuid.UUID,
    export_format: str,
    current_user=Depends(get_active_user),
    project_repo=Depends(get_project_repository),
    agg_service=Depends(get_aggregation_service),
    export_service=Depends(get_export_service),
):
    """Exports raw metrics table as a downloadable JSON or CSV format."""
    project = await project_repo.get_by_id_and_user_id(project_id, current_user.id)
    if not project:
        raise NotFoundException("Project not found or access denied.")

    if export_format.lower() not in ["json", "csv"]:
        raise ValidationException("Supported export formats: 'json', 'csv'.")

    summary = await agg_service.aggregate_project_summary(project_id)
    
    # Flatten metrics map for CSV formatting
    flat_metrics = {
        "datasets_count": summary["datasets_count"],
        "preprocessing_runs_count": summary["preprocessing_runs_count"],
        "training_sessions_count": summary["training_sessions_count"],
        "registered_models_count": summary["registered_models_count"],
        "storage_usage_bytes": summary["storage_usage_bytes"],
    }
    for k, v in summary.get("metrics_averages", {}).items():
        flat_metrics[f"avg_{k}"] = v

    if export_format.lower() == "json":
        content = export_service.to_json(summary)
    else:
        content = export_service.to_csv(flat_metrics)

    return ExportResponse(
        project_id=project_id,
        export_format=export_format,
        content=content,
        filename=f"opticrop_project_{project_id}_analytics.{export_format}",
    )
