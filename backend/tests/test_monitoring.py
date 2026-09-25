import uuid
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from httpx import AsyncClient

from app.core.enums import AlertStatus, DriftStatus
from app.models.project import Project
from app.models.dataset import Dataset
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.models.alert_rule import AlertRule
from app.models.monitoring_alert import MonitoringAlert
from app.models.drift_snapshot import DriftSnapshot
from app.repositories.sqlalchemy.user import SqlAlchemyUserRepository


async def get_auth_headers(client, email: str = "monitor_farmer@example.com", password: str = "SecurePassword123!") -> dict:
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Monitor Farmer",
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
    await get_auth_headers(client, "monitor_farmer@example.com")
    user_repo = SqlAlchemyUserRepository(db_session)
    user = await user_repo.get_by_email("monitor_farmer@example.com")
    return user


@pytest_asyncio.fixture
async def test_project(db_session, test_user_db):
    project = Project(
        id=uuid.uuid4(),
        user_id=test_user_db.id,
        name="Monitoring Test Project",
        description="Drifts and alerts tracking",
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
        name="yield_data",
        original_filename="yield_data.csv",
        stored_filename="yield_data_stored.csv",
        storage_path="datasets/yield_data_stored.csv",
        status="VALIDATED",
        version=1,
        size=1024,
    )
    db_session.add(dataset)
    await db_session.flush()
    await db_session.commit()
    return dataset


@pytest_asyncio.fixture
async def test_model(db_session, test_user_db, test_dataset, test_project):
    session_record = TrainingSession(
        id=uuid.uuid4(),
        dataset_id=test_dataset.id,
        user_id=test_user_db.id,
        problem_type="classification",
        target_column="crop_yield",
        status="COMPLETED",
        config_hash="confhash_mon",
    )
    db_session.add(session_record)
    await db_session.flush()

    model = TrainedModel(
        id=uuid.uuid4(),
        training_session_id=session_record.id,
        model_name="RandomForestClassifier_mon",
        algorithm="RandomForestClassifier",
        storage_path="models/rf_mon.joblib",
        version=1,
        is_active=True,
        status="READY",
        checksum="checksumrf_mon",
        signature={
            "feature_names": ["temperature", "water_index"],
            "feature_count": 2,
            "target_column": "crop_yield",
            "expected_dtypes": {
                "temperature": "float64",
                "water_index": "float64"
            }
        },
    )
    db_session.add(model)
    await db_session.flush()
    await db_session.commit()
    return model


# --- TESTS ---

@pytest.mark.asyncio
async def test_monitoring_health_endpoint(client: AsyncClient):
    headers = await get_auth_headers(client)
    response = await client.get("/api/v1/monitoring/health", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "unhealthy"]


@pytest.mark.asyncio
async def test_monitoring_overview(client: AsyncClient, test_project):
    headers = await get_auth_headers(client)
    response = await client.get("/api/v1/monitoring/overview", headers=headers)
    assert response.status_code == 200
    assert "total_predictions" in response.json()


@pytest.mark.asyncio
async def test_telemetry_ingest_validated_normalized(client: AsyncClient, test_project):
    headers = await get_auth_headers(client)
    payload = {
        "provider_name": "WeatherAPI",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "payload": {
            "temperature": 25.5,
            "humidity": 60.0
        }
    }
    response = await client.post(
        f"/api/v1/monitoring/telemetry/ingest?project_id={test_project.id}",
        json=payload,
        headers=headers
    )
    assert response.status_code == 201
    assert "record_id" in response.json()


@pytest.mark.asyncio
async def test_create_alert_rule(client: AsyncClient, test_project):
    headers = await get_auth_headers(client)
    payload = {
        "metric_name": "Latency",
        "threshold_value": 150.0,
        "comparison_operator": ">",
        "is_active": True
    }
    response = await client.post(
        f"/api/v1/monitoring/rules?project_id={test_project.id}",
        json=payload,
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["metric_name"] == "Latency"


@pytest.mark.asyncio
async def test_alert_rule_deduplication(client: AsyncClient, db_session, test_project, test_model):
    # Seed alert rule
    rule = AlertRule(
        project_id=test_project.id,
        metric_name="Latency",
        threshold_value=100.0,
        comparison_operator=">",
        is_active=True
    )
    db_session.add(rule)
    await db_session.flush()

    # Trigger alerts evaluation twice via service
    from app.services.monitoring.alerts import AlertsService
    from app.repositories.sqlalchemy.alert import SqlAlchemyAlertRepository
    
    alert_repo = SqlAlchemyAlertRepository(db_session)
    alerts_s = AlertsService(alert_repo)
    
    # 1. Trigger first alert
    a1 = await alerts_s.evaluate_and_trigger(
        test_project.id, test_model.id, rule, 120.0, "Latency exceeded threshold."
    )
    assert a1 is not None
    assert a1.occurrence_count == 1

    # 2. Trigger second alert (should deduplicate and increment occurrence_count)
    a2 = await alerts_s.evaluate_and_trigger(
        test_project.id, test_model.id, rule, 130.0, "Latency exceeded threshold."
    )
    assert a2 is not None
    assert a2.id == a1.id
    assert a2.occurrence_count == 2
    
    await db_session.commit()


@pytest.mark.asyncio
async def test_model_drift_calculation(client: AsyncClient, test_model):
    headers = await get_auth_headers(client)
    response = await client.get(
        f"/api/v1/monitoring/drift/{test_model.id}?algorithm=PSI",
        headers=headers
    )
    assert response.status_code == 200
    assert "overall_drift_score" in response.json()
    assert response.json()["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_monitoring_diagnostics_snapshot(client: AsyncClient, test_project, test_model):
    headers = await get_auth_headers(client)
    response = await client.get(
        f"/api/v1/monitoring/project/{test_project.id}?model_id={test_model.id}",
        headers=headers
    )
    assert response.status_code == 200
    assert "health" in response.json()
    assert "overall_status" in response.json()["health"]


@pytest.mark.asyncio
async def test_monitoring_alerts_export(client: AsyncClient, test_project):
    headers = await get_auth_headers(client)
    response = await client.get(
        f"/api/v1/monitoring/export/csv?project_id={test_project.id}",
        headers=headers
    )
    assert response.status_code == 200
    assert "alert_id,rule_name" in response.json()["content"]


@pytest.mark.asyncio
async def test_monitoring_isolation_boundaries(client: AsyncClient, test_project):
    # Authenticate User B
    headers_b = await get_auth_headers(client, "monitor_farmer_b@example.com", "SecurePassword999!")
    
    # User B queries User A's monitoring snapshot
    response = await client.get(
        f"/api/v1/monitoring/project/{test_project.id}?model_id={uuid.uuid4()}",
        headers=headers_b
    )
    assert response.status_code == 404
