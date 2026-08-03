import io
import uuid
import pytest
import pytest_asyncio
import joblib
import os
from httpx import AsyncClient

from app.core.enums import DatasetStatus, DatasetStage
from app.models.project import Project
from app.models.dataset import Dataset
from app.models.dataset_preprocessing import DatasetPreprocessing
from app.models.preprocessing_artifact import PreprocessingArtifact
from app.models.feature_metadata import FeatureMetadata
from app.repositories.sqlalchemy.user import SqlAlchemyUserRepository


async def get_auth_headers(client, email: str = "prepfarmer@example.com", password: str = "SecurePassword123!") -> dict:
    """Helper to authenticate a user session and return HTTP Headers."""
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Preprocessing Farmer",
    })
    payload = {"email": email, "password": password}
    response = await client.post("/api/v1/auth/login", json=payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_storage_service(monkeypatch):
    """Mocks Supabase storage client upload, download, and delete calls."""
    async def mock_upload(self, storage_path, file_path, content_type="text/csv"):
        return storage_path

    async def mock_download(self, storage_path):
        return (
            b"soil_ph,crop_type,temperature,crop_yield\n"
            b"6.5,Wheat,25.0,200\n"
            b",Corn,30.0,250\n"
            b"7.2,Wheat,28.0,220\n"
            b"6.0,Rice,24.0,180\n"
        )

    async def mock_delete(self, storage_path):
        return None

    monkeypatch.setattr("app.services.dataset.storage.StorageService.upload_file", mock_upload)
    monkeypatch.setattr("app.services.dataset.storage.StorageService.download_file", mock_download)
    monkeypatch.setattr("app.services.dataset.storage.StorageService.delete_file", mock_delete)


@pytest_asyncio.fixture
async def db_session():
    """Provides a database session bound to the in-memory SQLite engine."""
    from tests.conftest import test_session
    async with test_session() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def test_user_db(db_session, client):
    """Retrieves the database User instance for the registered test farmer."""
    await get_auth_headers(client, "prepfarmer@example.com")
    user_repo = SqlAlchemyUserRepository(db_session)
    user = await user_repo.get_by_email("prepfarmer@example.com")
    return user


@pytest_asyncio.fixture
async def test_project(db_session, test_user_db):
    """Creates a temporary project bound to the test user."""
    project = Project(
        id=uuid.uuid4(),
        user_id=test_user_db.id,
        name="Test Prep Project",
        description="Preprocessing Experiment Workspace",
    )
    db_session.add(project)
    await db_session.flush()
    await db_session.commit()
    return project


@pytest_asyncio.fixture
async def test_dataset(db_session, test_user_db, test_project):
    """Creates a validated raw dataset inside the DB."""
    dataset = Dataset(
        id=uuid.uuid4(),
        project_id=test_project.id,
        user_id=test_user_db.id,
        name="raw_agri_data",
        original_filename="raw_agri_data.csv",
        stored_filename="raw_stored.csv",
        storage_path="datasets/raw_stored.csv",
        status=DatasetStatus.VALIDATED,
        dataset_stage=DatasetStage.RAW,
        is_latest=True,
        delimiter=",",
        encoding="utf-8",
    )
    db_session.add(dataset)
    await db_session.flush()
    await db_session.commit()
    return dataset


@pytest.mark.asyncio
async def test_trigger_preprocessing_pipeline(client: AsyncClient, test_dataset, test_project):
    headers = await get_auth_headers(client, "prepfarmer@example.com")
    
    config = {
        "target_column": "crop_yield",
        "missing_value_strategies": {
            "numeric_strategy": "mean",
            "categorical_strategy": "most_frequent"
        },
        "outlier_strategy": {
            "method": "IQR",
            "action": "flag_only"
        },
        "encoding_mappings": {
            "crop_type": "OneHotEncoder"
        },
        "scaling_mappings": {
            "temperature": "StandardScaler"
        }
    }
    
    response = await client.post(
        f"/api/v1/preprocessing/?dataset_id={test_dataset.id}&project_id={test_project.id}",
        json=config,
        headers=headers
    )
    
    assert response.status_code == 202
    res_data = response.json()
    assert res_data["status"] == "PENDING"
    assert res_data["preprocessing_hash"] != ""


@pytest.mark.asyncio
async def test_duplicate_run_reusability(client: AsyncClient, db_session, test_dataset, test_project, test_user_db):
    headers = await get_auth_headers(client, "prepfarmer@example.com")
    
    config = {
        "target_column": "crop_yield",
        "missing_value_strategies": {
            "numeric_strategy": "median",
            "categorical_strategy": "most_frequent",
            "columns_overrides": {}
        },
        "outlier_strategy": {
            "method": "IQR",
            "action": "flag_only"
        },
        "encoding_mappings": {},
        "scaling_mappings": {}
    }
    import json, hashlib
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    
    # Pre-seed a completed run configuration
    existing_run = DatasetPreprocessing(
        id=uuid.uuid4(),
        dataset_id=test_dataset.id,
        user_id=test_user_db.id,
        project_id=test_project.id,
        status="COMPLETED",
        parameters=config,
        preprocessing_hash=config_hash,
        pipeline_version=1,
        python_version="3.11",
        pandas_version="2.0",
        numpy_version="1.24",
        sklearn_version="1.4",
    )
    db_session.add(existing_run)
    await db_session.flush()
    await db_session.commit()

    response = await client.post(
        f"/api/v1/preprocessing/?dataset_id={test_dataset.id}&project_id={test_project.id}",
        json=config,
        headers=headers
    )
    assert response.status_code == 202
    assert response.json()["id"] == str(existing_run.id)  # Enforces duplicate config run reuse!


@pytest.mark.asyncio
async def test_execute_pipeline_verification(client: AsyncClient, db_session, test_dataset, test_project):
    headers = await get_auth_headers(client, "prepfarmer@example.com")
    
    config = {
        "target_column": "crop_yield",
        "missing_value_strategies": {
            "numeric_strategy": "median",
            "categorical_strategy": "most_frequent"
        },
        "outlier_strategy": {
            "method": "IQR",
            "action": "flag_only"
        },
        "encoding_mappings": {
            "crop_type": "OneHotEncoder"
        },
        "scaling_mappings": {
            "temperature": "StandardScaler"
        }
    }
    
    response = await client.post(
        f"/api/v1/preprocessing/?dataset_id={test_dataset.id}&project_id={test_project.id}",
        json=config,
        headers=headers
    )
    assert response.status_code == 202
    run_id = uuid.UUID(response.json()["id"])
    
    # Fetch run completed details from db
    from app.repositories.sqlalchemy.preprocessing import SqlAlchemyPreprocessingRepository
    prep_repo = SqlAlchemyPreprocessingRepository(db_session)
    
    run_obj = await prep_repo.get_by_id(run_id)
    assert run_obj is not None
    assert run_obj.status == "COMPLETED"
    assert run_obj.preprocessed_dataset_id is not None
    
    # Verify that Preprocessed Dataset version is registered
    preprocessed_dataset = await db_session.get(Dataset, run_obj.preprocessed_dataset_id)
    assert preprocessed_dataset is not None
    assert preprocessed_dataset.dataset_stage == DatasetStage.PREPROCESSED
    assert preprocessed_dataset.version == 2
    
    # Verify that PreprocessingArtifact entry is created
    assert len(run_obj.artifacts) == 2  # temperature (StandardScaler), crop_type (OneHotEncoder)
    
    # Verify that FeatureMetadata catalog is populated
    from app.repositories.sqlalchemy.feature import SqlAlchemyFeatureMetadataRepository
    feat_repo = SqlAlchemyFeatureMetadataRepository(db_session)
    features = await feat_repo.get_by_dataset_id(preprocessed_dataset.id)
    assert len(features) > 0
    
    target_feature = [f for f in features if f.target][0]
    assert target_feature.feature_name == "crop_yield"
    assert target_feature.feature_type == "TARGET"


@pytest.mark.asyncio
async def test_invalid_target_fails_pipeline(client: AsyncClient, db_session, test_dataset, test_project):
    headers = await get_auth_headers(client, "prepfarmer@example.com")
    config = {"target_column": "missing_target"}
    
    response = await client.post(
        f"/api/v1/preprocessing/?dataset_id={test_dataset.id}&project_id={test_project.id}",
        json=config,
        headers=headers
    )
    assert response.status_code == 202
    run_id = uuid.UUID(response.json()["id"])
    
    from app.repositories.sqlalchemy.preprocessing import SqlAlchemyPreprocessingRepository
    prep_repo = SqlAlchemyPreprocessingRepository(db_session)
    run_obj = await prep_repo.get_by_id(run_id)
    assert run_obj is not None
    assert run_obj.status == "FAILED"
    assert "missing" in run_obj.error_message
