import uuid
import pytest
import pytest_asyncio
import numpy as np
from httpx import AsyncClient

from app.core.enums import DatasetStatus, DatasetStage
from app.models.project import Project
from app.models.dataset import Dataset
from app.models.feature_metadata import FeatureMetadata
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.models.prediction_run import PredictionRun, PredictionStatus
from app.repositories.sqlalchemy.user import SqlAlchemyUserRepository


class MockEstimator:
    def predict(self, X):
        return np.ones(len(X))

    def predict_proba(self, X):
        return np.array([[0.1, 0.9] for _ in range(len(X))])


class MockTransformer:
    def transform(self, X):
        return X


async def get_auth_headers(client, email: str = "pred_farmer@example.com", password: str = "SecurePassword123!") -> dict:
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Prediction Farmer",
    })
    payload = {"email": email, "password": password}
    response = await client.post("/api/v1/auth/login", json=payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_predictions_serialization(monkeypatch):
    async def mock_download_and_verify(self, storage_path, expected_checksum):
        if "scaler" in storage_path or "encoder" in storage_path:
            return MockTransformer()
        return MockEstimator()
    monkeypatch.setattr(
        "app.services.prediction.serialization.PredictionSerializationService.download_and_verify",
        mock_download_and_verify
    )


@pytest_asyncio.fixture
async def db_session():
    from tests.conftest import test_session
    async with test_session() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def test_user_db(db_session, client):
    await get_auth_headers(client, "pred_farmer@example.com")
    user_repo = SqlAlchemyUserRepository(db_session)
    user = await user_repo.get_by_email("pred_farmer@example.com")
    return user


@pytest_asyncio.fixture
async def test_project(db_session, test_user_db):
    project = Project(
        id=uuid.uuid4(),
        user_id=test_user_db.id,
        name="Prediction Test Project",
        description="Real-time and batch inferences",
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
async def test_trained_model(db_session, test_user_db, test_dataset, test_project):
    session_record = TrainingSession(
        id=uuid.uuid4(),
        dataset_id=test_dataset.id,
        experiment_id=None,
        preprocessing_run_id=None,
        user_id=test_user_db.id,
        problem_type="classification",
        target_column="crop_type",
        status="COMPLETED",
        config={"problem_type": "classification"},
        training_seed=42,
        test_size=0.2,
        shuffle=True,
        cv_seed=42,
        config_hash="confhash123",
        best_model="RandomForestClassifier_model",
        training_time=5.5,
    )
    db_session.add(session_record)
    await db_session.flush()

    trained_model = TrainedModel(
        id=uuid.uuid4(),
        training_session_id=session_record.id,
        model_name="RandomForestClassifier_model",
        algorithm="RandomForestClassifier",
        storage_path="models/rf.joblib",
        version=1,
        is_active=True,
        status="READY",
        checksum="checksumrf",
        hyperparameters={"n_estimators": 10},
        signature={
            "feature_names": ["temperature", "water_index"],
            "feature_count": 2,
            "target_column": "crop_type",
            "expected_dtypes": {
                "temperature": "float64",
                "water_index": "float64"
            }
        },
    )
    db_session.add(trained_model)
    await db_session.flush()
    await db_session.commit()
    return trained_model


# --- TESTS ---

@pytest.mark.asyncio
async def test_predictions_health(client: AsyncClient):
    headers = await get_auth_headers(client)
    response = await client.get("/api/v1/predictions/health", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_single_prediction_success(client: AsyncClient, test_project, test_trained_model):
    headers = await get_auth_headers(client)
    payload = {
        "project_id": str(test_project.id),
        "features": {
            "temperature": 23.5,
            "water_index": 0.62
        }
    }
    response = await client.post("/api/v1/predictions/", json=payload, headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["predictions"] == [1.0]
    assert json_data["confidence_scores"] == [0.9]


@pytest.mark.asyncio
async def test_single_prediction_validation_failure(client: AsyncClient, test_project, test_trained_model):
    headers = await get_auth_headers(client)
    # Send missing field
    payload = {
        "project_id": str(test_project.id),
        "features": {
            "temperature": 23.5
        }
    }
    response = await client.post("/api/v1/predictions/", json=payload, headers=headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_batch_prediction_async_trigger(client: AsyncClient, test_project, test_trained_model):
    headers = await get_auth_headers(client)
    payload = {
        "project_id": str(test_project.id),
        "features_list": [
            {"temperature": 23.5, "water_index": 0.62},
            {"temperature": 24.5, "water_index": 0.68}
        ]
    }
    response = await client.post("/api/v1/predictions/batch", json=payload, headers=headers)
    assert response.status_code == 202
    assert response.json()["status"] == "PENDING"
    assert response.json()["prediction_count"] == 2


@pytest.mark.asyncio
async def test_idempotency_validation(client: AsyncClient, test_project, test_trained_model):
    headers = await get_auth_headers(client)
    idempotency_key = "uniq-idem-key-123"
    
    payload = {
        "project_id": str(test_project.id),
        "features": {
            "temperature": 23.5,
            "water_index": 0.62
        }
    }
    
    # Request 1
    res1 = await client.post(
        "/api/v1/predictions/",
        json=payload,
        headers={**headers, "Idempotency-Key": idempotency_key}
    )
    assert res1.status_code == 200
    
    # Request 2 (should hit idempotency key and return same prediction ID)
    res2 = await client.post(
        "/api/v1/predictions/",
        json=payload,
        headers={**headers, "Idempotency-Key": idempotency_key}
    )
    assert res2.status_code == 200
    assert res1.json()["prediction_id"] == res2.json()["prediction_id"]


@pytest.mark.asyncio
async def test_predictions_history(client: AsyncClient, test_project, test_trained_model):
    headers = await get_auth_headers(client)
    payload = {
        "project_id": str(test_project.id),
        "features": {
            "temperature": 23.5,
            "water_index": 0.62
        }
    }
    await client.post("/api/v1/predictions/", json=payload, headers=headers)
    
    # Get history
    history_res = await client.get(f"/api/v1/predictions/history?project_id={test_project.id}", headers=headers)
    assert history_res.status_code == 200
    assert len(history_res.json()) >= 1


@pytest.mark.asyncio
async def test_predictions_export(client: AsyncClient, test_project, test_trained_model):
    headers = await get_auth_headers(client)
    # Trigger prediction
    payload = {
        "project_id": str(test_project.id),
        "features": {
            "temperature": 23.5,
            "water_index": 0.62
        }
    }
    await client.post("/api/v1/predictions/", json=payload, headers=headers)
    
    # Export
    export_res = await client.get(f"/api/v1/predictions/export/csv?project_id={test_project.id}", headers=headers)
    assert export_res.status_code == 200
    assert "prediction_id,project_id" in export_res.json()["content"]


@pytest.mark.asyncio
async def test_prediction_security_boundaries(client: AsyncClient, test_project, test_trained_model):
    # Authenticate User B
    headers_b = await get_auth_headers(client, "pred_farmer_b@example.com", "SecurePassword999!")
    
    # User B triggers predictions on User A's project
    payload = {
        "project_id": str(test_project.id),
        "features": {
            "temperature": 23.5,
            "water_index": 0.62
        }
    }
    response = await client.post("/api/v1/predictions/", json=payload, headers=headers_b)
    assert response.status_code == 404
