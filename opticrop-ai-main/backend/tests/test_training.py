import uuid
import pytest
import pytest_asyncio
import joblib
import json
import hashlib
from datetime import datetime, timezone
from httpx import AsyncClient

from app.core.enums import DatasetStatus, DatasetStage
from app.models.project import Project
from app.models.dataset import Dataset
from app.models.feature_metadata import FeatureMetadata
from app.models.training_experiment import TrainingExperiment
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.models.evaluation_report import EvaluationReport
from app.repositories.sqlalchemy.user import SqlAlchemyUserRepository


async def get_auth_headers(client, email: str = "trainfarmer@example.com", password: str = "SecurePassword123!") -> dict:
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Training Farmer",
    })
    payload = {"email": email, "password": password}
    response = await client.post("/api/v1/auth/login", json=payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_storage_service(monkeypatch):
    async def mock_upload(self, storage_path, file_path, content_type="text/csv"):
        return storage_path

    async def mock_download(self, storage_path):
        # 12 samples (satisfies limit >= 10), regression problem (target: crop_yield)
        lines = [
            "temperature,water_index,crop_yield",
            "20.0,0.5,150",
            "21.0,0.6,160",
            "22.0,0.5,155",
            "23.0,0.7,170",
            "24.0,0.6,165",
            "25.0,0.8,180",
            "26.0,0.5,175",
            "27.0,0.7,190",
            "28.0,0.6,185",
            "29.0,0.9,200",
            "30.0,0.8,195",
            "31.0,0.7,210"
        ]
        return "\n".join(lines).encode()

    async def mock_delete(self, storage_path):
        return None

    monkeypatch.setattr("app.services.dataset.storage.StorageService.upload_file", mock_upload)
    monkeypatch.setattr("app.services.dataset.storage.StorageService.download_file", mock_download)
    monkeypatch.setattr("app.services.dataset.storage.StorageService.delete_file", mock_delete)


@pytest_asyncio.fixture
async def db_session():
    from tests.conftest import test_session
    async with test_session() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def test_user_db(db_session, client):
    await get_auth_headers(client, "trainfarmer@example.com")
    user_repo = SqlAlchemyUserRepository(db_session)
    user = await user_repo.get_by_email("trainfarmer@example.com")
    return user


@pytest_asyncio.fixture
async def test_project(db_session, test_user_db):
    project = Project(
        id=uuid.uuid4(),
        user_id=test_user_db.id,
        name="Test Train Project",
        description="Training Registry Experiments",
    )
    db_session.add(project)
    await db_session.flush()
    await db_session.commit()
    return project


@pytest_asyncio.fixture
async def test_dataset(db_session, test_user_db, test_project):
    # Register dataset version as preprocessed and validated
    dataset = Dataset(
        id=uuid.uuid4(),
        project_id=test_project.id,
        user_id=test_user_db.id,
        name="clean_agri_data",
        original_filename="clean_agri_data.csv",
        stored_filename="clean_stored.csv",
        storage_path="datasets/clean_stored.csv",
        status=DatasetStatus.VALIDATED,
        dataset_stage=DatasetStage.PREPROCESSED,
        is_latest=True,
        delimiter=",",
        encoding="utf-8",
        sha256_checksum="mockchecksumhash",
        version=1,
    )
    db_session.add(dataset)
    await db_session.flush()

    # Pre-seed target column and numeric features catalog
    features = [
        FeatureMetadata(id=uuid.uuid4(), dataset_id=dataset.id, feature_name="temperature", feature_type="NUMERIC", nullable=False, encoded=False, scaled=False, generated=False, target=False),
        FeatureMetadata(id=uuid.uuid4(), dataset_id=dataset.id, feature_name="water_index", feature_type="NUMERIC", nullable=False, encoded=False, scaled=False, generated=False, target=False),
        FeatureMetadata(id=uuid.uuid4(), dataset_id=dataset.id, feature_name="crop_yield", feature_type="TARGET", nullable=False, encoded=False, scaled=False, generated=False, target=True),
    ]
    for feat in features:
        db_session.add(feat)

    await db_session.flush()
    await db_session.commit()
    return dataset


@pytest_asyncio.fixture
async def test_experiment(db_session, test_project):
    experiment = TrainingExperiment(
        id=uuid.uuid4(),
        project_id=test_project.id,
        name="Base Regression Run",
        description="Search optimal model configurations",
    )
    db_session.add(experiment)
    await db_session.flush()
    await db_session.commit()
    return experiment


@pytest.mark.asyncio
async def test_create_experiment(client: AsyncClient, test_project):
    headers = await get_auth_headers(client, "trainfarmer@example.com")
    
    payload = {
        "project_id": str(test_project.id),
        "name": "Decision Tree Regression",
        "description": "Fit Decision Trees on yield datasets",
    }
    
    response = await client.post("/api/v1/training/experiments", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Decision Tree Regression"


@pytest.mark.asyncio
async def test_trigger_training_session(client: AsyncClient, test_dataset, test_experiment, test_project):
    headers = await get_auth_headers(client, "trainfarmer@example.com")
    
    payload = {
        "experiment_id": str(test_experiment.id),
        "dataset_id": str(test_dataset.id),
        "problem_type": "regression",
        "algorithms": ["LinearRegression", "RandomForestRegressor"],
        "hyperparameters": {
            "RandomForestRegressor": {
                "n_estimators": [5, 10],
            }
        },
        "cv_strategy": {
            "method": "KFold",
            "folds": 3
        },
        "training_seed": 42,
        "test_size": 0.2
    }
    
    response = await client.post(
        f"/api/v1/training/?dataset_id={test_dataset.id}&project_id={test_project.id}",
        json=payload,
        headers=headers
    )
    assert response.status_code == 202
    assert response.json()["status"] == "PENDING"
    assert response.json()["config_hash"] != ""


@pytest.mark.asyncio
async def test_duplicate_training_cached(client: AsyncClient, db_session, test_dataset, test_experiment, test_project, test_user_db):
    headers = await get_auth_headers(client, "trainfarmer@example.com")
    
    payload = {
        "experiment_id": str(test_experiment.id),
        "dataset_id": str(test_dataset.id),
        "problem_type": "regression",
        "algorithms": ["LinearRegression"],
        "hyperparameters": {},
        "cv_strategy": {
            "method": "KFold",
            "folds": 5
        },
        "training_seed": 42,
        "test_size": 0.2,
        "shuffle": True
    }
    
    # Calculate config hash
    hash_payload = f"1:no_prep:['LinearRegression']:{json.dumps({}, sort_keys=True)}:{json.dumps({'method': 'KFold', 'folds': 5}, sort_keys=True)}:42:0.2:True"
    config_hash = hashlib.sha256(hash_payload.encode()).hexdigest()

    existing_run = TrainingSession(
        id=uuid.uuid4(),
        dataset_id=test_dataset.id,
        experiment_id=test_experiment.id,
        user_id=test_user_db.id,
        problem_type="regression",
        target_column="crop_yield",
        status="COMPLETED",
        config_hash=config_hash,
    )
    db_session.add(existing_run)
    await db_session.flush()
    await db_session.commit()

    response = await client.post(
        f"/api/v1/preprocessing/?dataset_id={test_dataset.id}&project_id={test_project.id}",
        json=payload,
        headers=headers
    )
    # The API will trigger the duplicate config check inside initiate_run and reuse the pre-seeded completed session
    response = await client.post(
        f"/api/v1/training/?dataset_id={test_dataset.id}&project_id={test_project.id}",
        json=payload,
        headers=headers
    )
    assert response.status_code == 202
    assert response.json()["id"] == str(existing_run.id)


@pytest.mark.asyncio
async def test_execute_training_pipeline_and_evaluate(client: AsyncClient, db_session, test_dataset, test_experiment, test_project):
    headers = await get_auth_headers(client, "trainfarmer@example.com")
    
    payload = {
        "experiment_id": str(test_experiment.id),
        "dataset_id": str(test_dataset.id),
        "problem_type": "regression",
        "algorithms": ["LinearRegression"],
        "hyperparameters": {},
        "cv_strategy": {
            "method": "KFold",
            "folds": 3
        },
        "training_seed": 42,
        "test_size": 0.2
    }
    
    response = await client.post(
        f"/api/v1/training/?dataset_id={test_dataset.id}&project_id={test_project.id}",
        json=payload,
        headers=headers
    )
    assert response.status_code == 202
    session_id = uuid.UUID(response.json()["id"])
    
    from app.repositories.sqlalchemy.training_session import SqlAlchemyTrainingSessionRepository
    sess_repo = SqlAlchemyTrainingSessionRepository(db_session)
    run_obj = await sess_repo.get_by_id(session_id)
    
    assert run_obj is not None
    assert run_obj.status == "COMPLETED"
    assert run_obj.best_model != ""
    assert run_obj.storage_model_path != ""

    # Verify model registry creation
    from app.repositories.sqlalchemy.trained_model import SqlAlchemyTrainedModelRepository
    model_repo = SqlAlchemyTrainedModelRepository(db_session)
    models = await model_repo.get_by_project_id(test_project.id)
    
    assert len(models) == 1
    model = models[0]
    assert model.status == "READY"
    assert model.is_active is False
    assert model.signature["feature_count"] == 2
    assert model.signature["target_column"] == "crop_yield"

    # Verify evaluation report (with residuals and rankings)
    assert model.evaluation_report is not None
    report = model.evaluation_report.report_data
    assert "comparison_table" in report
    assert "residuals" in report["winner_visuals"]


@pytest.mark.asyncio
async def test_model_activation_registry_transaction(client: AsyncClient, db_session, test_dataset, test_experiment, test_project, test_user_db):
    headers = await get_auth_headers(client, "trainfarmer@example.com")
    
    # Pre-seed session
    session_rec = TrainingSession(
        id=uuid.uuid4(),
        dataset_id=test_dataset.id,
        experiment_id=test_experiment.id,
        user_id=test_user_db.id,
        problem_type="regression",
        target_column="crop_yield",
        status="COMPLETED"
    )
    db_session.add(session_rec)
    await db_session.flush()

    # Pre-seed two trained models
    model1 = TrainedModel(
        id=uuid.uuid4(),
        training_session_id=session_rec.id,
        model_name="model1",
        algorithm="LinearRegression",
        storage_path="models/m1.joblib",
        is_active=True,
        status="READY"
    )
    model2 = TrainedModel(
        id=uuid.uuid4(),
        training_session_id=session_rec.id,
        model_name="model2",
        algorithm="RandomForest",
        storage_path="models/m2.joblib",
        is_active=False,
        status="READY"
    )
    db_session.add(model1)
    db_session.add(model2)
    await db_session.flush()
    await db_session.commit()

    # Activate Model 2 - checks that Model 1 gets deactivated automatically
    response = await client.post(
        f"/api/v1/training/models/{model2.id}/activate?project_id={test_project.id}",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is True

    # Check database state
    await db_session.refresh(model1)
    await db_session.refresh(model2)
    assert model1.is_active is False
    assert model2.is_active is True
