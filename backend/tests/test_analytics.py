import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.core.enums import DatasetStatus, DatasetStage
from app.models.project import Project
from app.models.dataset import Dataset
from app.models.feature_metadata import FeatureMetadata
from app.models.training_experiment import TrainingExperiment
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.models.evaluation_report import EvaluationReport
from app.models.model_metric import ModelMetric
from app.repositories.sqlalchemy.user import SqlAlchemyUserRepository


async def get_auth_headers(client, email: str = "analytics_farmer@example.com", password: str = "SecurePassword123!") -> dict:
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Analytics Farmer",
    })
    payload = {"email": email, "password": password}
    response = await client.post("/api/v1/auth/login", json=payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def db_session():
    from tests.conftest import test_session
    async with test_session() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def test_user_db(db_session, client):
    await get_auth_headers(client, "analytics_farmer@example.com")
    user_repo = SqlAlchemyUserRepository(db_session)
    user = await user_repo.get_by_email("analytics_farmer@example.com")
    return user


@pytest_asyncio.fixture
async def test_project(db_session, test_user_db):
    project = Project(
        id=uuid.uuid4(),
        user_id=test_user_db.id,
        name="Analytics Test Project",
        description="Workspace overview metrics checks",
    )
    db_session.add(project)
    await db_session.flush()
    await db_session.commit()
    return project


@pytest_asyncio.fixture
async def test_dataset(db_session, test_user_db, test_project):
    dataset = Dataset(
        id=uuid.uuid4(),
        project_id=test_project.id,
        user_id=test_user_db.id,
        name="yield_raw_data",
        original_filename="yield_raw_data.csv",
        stored_filename="raw_stored.csv",
        storage_path="datasets/raw_stored.csv",
        status=DatasetStatus.VALIDATED,
        dataset_stage=DatasetStage.RAW,
        is_latest=True,
        delimiter=",",
        encoding="utf-8",
        sha256_checksum="check123hash",
        version=1,
        size=1024,
    )
    db_session.add(dataset)
    await db_session.flush()
    await db_session.commit()
    return dataset


@pytest_asyncio.fixture
async def test_training_session(db_session, test_user_db, test_dataset, test_project):
    experiment = TrainingExperiment(
        id=uuid.uuid4(),
        project_id=test_project.id,
        name="Crop Yield Regressions",
        description="Fitting various regressor models",
    )
    db_session.add(experiment)
    await db_session.flush()

    session_record = TrainingSession(
        id=uuid.uuid4(),
        dataset_id=test_dataset.id,
        experiment_id=experiment.id,
        preprocessing_run_id=None,
        user_id=test_user_db.id,
        problem_type="regression",
        target_column="crop_yield",
        status="COMPLETED",
        config={"problem_type": "regression"},
        training_seed=42,
        test_size=0.2,
        shuffle=True,
        cv_seed=42,
        config_hash="confhash123",
        best_model="RandomForestRegressor_model",
        training_time=5.5,
    )
    db_session.add(session_record)
    await db_session.flush()
    await db_session.commit()
    return session_record


@pytest_asyncio.fixture
async def test_trained_model(db_session, test_training_session):
    model_uuid = uuid.uuid4()
    trained_model = TrainedModel(
        id=model_uuid,
        training_session_id=test_training_session.id,
        model_name="RandomForestRegressor_model",
        algorithm="RandomForestRegressor",
        storage_path="models/rf.joblib",
        version=1,
        is_active=True,
        status="READY",
        checksum="checksumrf",
        hyperparameters={"n_estimators": 10},
        signature={
            "feature_names": ["temperature", "water_index"],
            "feature_count": 2,
            "target_column": "crop_yield"
        },
    )
    db_session.add(trained_model)
    await db_session.flush()

    metric = ModelMetric(
        id=uuid.uuid4(),
        trained_model_id=model_uuid,
        metric_name="r2",
        metric_value=0.88,
    )
    db_session.add(metric)
    
    report = EvaluationReport(
        id=uuid.uuid4(),
        trained_model_id=model_uuid,
        report_data={
            "winner_metrics": {"r2": 0.88},
            "winner_visuals": {
                "actual": [10.0, 20.0, 30.0],
                "predicted": [9.8, 19.5, 30.2],
                "feature_importances": {
                    "temperature": 0.65,
                    "water_index": 0.35
                }
            }
        }
    )
    db_session.add(report)
    await db_session.flush()
    await db_session.commit()
    return trained_model


# --- TESTS SUITE ---

@pytest.mark.asyncio
async def test_analytics_health(client: AsyncClient):
    headers = await get_auth_headers(client, "analytics_farmer@example.com")
    response = await client.get("/api/v1/analytics/health", headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["cache"] == "healthy"
    assert json_data["api_version"] == "v1"


@pytest.mark.asyncio
async def test_project_overview_dashboard(client: AsyncClient, test_project, test_trained_model):
    headers = await get_auth_headers(client, "analytics_farmer@example.com")
    response = await client.get(f"/api/v1/analytics/project/{test_project.id}/overview", headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["datasets_count"] == 1
    assert json_data["registered_models_count"] == 1
    assert json_data["active_model"]["id"] == str(test_trained_model.id)
    assert len(json_data["recent_activity"]) > 0


@pytest.mark.asyncio
async def test_dataset_lineage_dag(client: AsyncClient, test_project, test_dataset):
    headers = await get_auth_headers(client, "analytics_farmer@example.com")
    response = await client.get(f"/api/v1/analytics/project/{test_project.id}/lineage", headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data["nodes"]) == 1
    assert json_data["nodes"][0]["label"] == "yield_raw_data (v1)"


@pytest.mark.asyncio
async def test_model_metrics_comparison(client: AsyncClient, test_project, test_trained_model):
    headers = await get_auth_headers(client, "analytics_farmer@example.com")
    compare_url = f"/api/v1/analytics/project/{test_project.id}/compare?model_ids={test_trained_model.id}"
    response = await client.get(compare_url, headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data["comparison_table"]) == 1
    assert json_data["comparison_table"][0]["algorithm"] == "RandomForestRegressor"
    assert json_data["hyperparameters_comparison"][str(test_trained_model.id)]["n_estimators"] == 10


@pytest.mark.asyncio
async def test_model_evaluation_visual_plots(client: AsyncClient, test_trained_model):
    headers = await get_auth_headers(client, "analytics_farmer@example.com")
    response = await client.get(f"/api/v1/analytics/models/{test_trained_model.id}/plots", headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data) == 1
    assert json_data[0]["chart_type"] == "scatter"  # Residuals plot
    assert json_data[0]["title"] == "Residuals Scatter Plot"


@pytest.mark.asyncio
async def test_model_feature_importances(client: AsyncClient, test_trained_model):
    headers = await get_auth_headers(client, "analytics_farmer@example.com")
    response = await client.get(f"/api/v1/analytics/models/{test_trained_model.id}/features", headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["chart_type"] == "bar"
    assert "temperature" in json_data["axes"]["x_categories"]


@pytest.mark.asyncio
async def test_project_summary_exporters(client: AsyncClient, test_project, test_trained_model):
    headers = await get_auth_headers(client, "analytics_farmer@example.com")
    # Test JSON export
    json_res = await client.get(f"/api/v1/analytics/project/{test_project.id}/export/json", headers=headers)
    assert json_res.status_code == 200
    assert json_res.json()["export_format"] == "json"
    
    # Test CSV export
    csv_res = await client.get(f"/api/v1/analytics/project/{test_project.id}/export/csv", headers=headers)
    assert csv_res.status_code == 200
    assert csv_res.json()["export_format"] == "csv"
    assert "datasets_count,1" in csv_res.json()["content"]


@pytest.mark.asyncio
async def test_security_isolation(client: AsyncClient, test_project):
    # Register separate user B
    headers_b = await get_auth_headers(client, "user_b@example.com", "SecurePassword999!")
    
    # User B requests User A's project dashboard
    response = await client.get(f"/api/v1/analytics/project/{test_project.id}/overview", headers=headers_b)
    assert response.status_code == 404
