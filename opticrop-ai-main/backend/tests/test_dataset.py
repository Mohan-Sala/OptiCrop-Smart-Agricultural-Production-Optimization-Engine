import io
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.core.enums import DatasetStatus, DatasetStage
from app.models.project import Project
from app.models.dataset import Dataset
from app.models.dataset_statistics import DatasetStatistics
from app.repositories.sqlalchemy.user import SqlAlchemyUserRepository


async def get_auth_headers(client, email: str = "datasetfarmer@example.com", password: str = "SecurePassword123!") -> dict:
    """Helper to authenticate a user session and return HTTP Headers."""
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Dataset Farmer",
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
        return b"col1,col2\nval1,val2\nval3,val4\n"

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
    await get_auth_headers(client, "datasetfarmer@example.com")
    user_repo = SqlAlchemyUserRepository(db_session)
    user = await user_repo.get_by_email("datasetfarmer@example.com")
    return user


@pytest_asyncio.fixture
async def test_project(db_session, test_user_db):
    """Creates a temporary project bound to the test user."""
    project = Project(
        id=uuid.uuid4(),
        user_id=test_user_db.id,
        name="Test ML Project",
        description="ML Experimentation Workspace",
    )
    db_session.add(project)
    await db_session.flush()
    await db_session.commit()
    return project


@pytest.mark.asyncio
async def test_upload_dataset_success(client: AsyncClient, db_session, test_user_db, test_project):
    headers = await get_auth_headers(client, "datasetfarmer@example.com")
    csv_content = b"feature1,feature2,label\n1.0,2.0,0\n3.0,4.0,1\n"
    
    # 1. Trigger dataset upload request
    response = await client.post(
        f"/api/v1/datasets/?project_id={test_project.id}&description=Test description&tags=tag1,tags2",
        files={"file": ("dataset.csv", csv_content, "text/csv")},
        headers=headers,
    )
    
    assert response.status_code == 202
    res_data = response.json()
    assert res_data["name"] == "dataset"
    assert res_data["status"] == DatasetStatus.UPLOADING
    assert res_data["dataset_stage"] == DatasetStage.RAW
    
    dataset_id = uuid.UUID(res_data["id"])

    # 2. Verify status updates to VALIDATED in db
    from app.repositories.sqlalchemy.dataset import SqlAlchemyDatasetRepository
    repo = SqlAlchemyDatasetRepository(db_session)
    dataset = await repo.get_by_id(dataset_id)
    
    assert dataset is not None
    assert dataset.status == DatasetStatus.VALIDATED
    assert dataset.rows == 2
    assert dataset.columns == 3
    assert dataset.delimiter == ","
    assert dataset.encoding == "ascii"
    
    # Check that analytical statistics table was successfully populated
    statistics = await db_session.get(DatasetStatistics, dataset.statistics.id) if dataset.statistics else None
    assert statistics is not None
    assert statistics.duplicate_rows == 0
    assert statistics.memory_usage > 0
    assert "feature1" in statistics.column_summary


@pytest.mark.asyncio
async def test_upload_dataset_invalid_extension(client: AsyncClient, test_project):
    headers = await get_auth_headers(client, "datasetfarmer@example.com")
    response = await client.post(
        f"/api/v1/datasets/?project_id={test_project.id}",
        files={"file": ("dataset.txt", b"some data", "text/plain")},
        headers=headers,
    )
    assert response.status_code == 400
    assert "only CSV file formats" in response.json()["message"]


@pytest.mark.asyncio
async def test_upload_dataset_duplicate_column_headers(client: AsyncClient, db_session, test_project):
    headers = await get_auth_headers(client, "datasetfarmer@example.com")
    csv_content = b"col1,col1,col2\n1.0,2.0,3.0\n"
    
    response = await client.post(
        f"/api/v1/datasets/?project_id={test_project.id}",
        files={"file": ("dataset.csv", csv_content, "text/csv")},
        headers=headers,
    )
    assert response.status_code == 202
    dataset_id = uuid.UUID(response.json()["id"])
    
    from app.repositories.sqlalchemy.dataset import SqlAlchemyDatasetRepository
    repo = SqlAlchemyDatasetRepository(db_session)
    dataset = await repo.get_by_id(dataset_id)
    assert dataset is not None
    assert dataset.status == DatasetStatus.FAILED


@pytest.mark.asyncio
async def test_list_datasets_paginated(client: AsyncClient, db_session, test_user_db, test_project):
    headers = await get_auth_headers(client, "datasetfarmer@example.com")
    
    # Seed 3 datasets manually
    for i in range(3):
        dataset = Dataset(
            id=uuid.uuid4(),
            project_id=test_project.id,
            user_id=test_user_db.id,
            name=f"dataset_{i}",
            original_filename=f"file_{i}.csv",
            stored_filename=f"stored_{i}.csv",
            storage_path=f"path_{i}.csv",
            status=DatasetStatus.VALIDATED,
            dataset_stage=DatasetStage.RAW,
            is_latest=True,
        )
        db_session.add(dataset)
    await db_session.flush()
    await db_session.commit()

    # Query listings
    response = await client.get(f"/api/v1/datasets/?project_id={test_project.id}&page=1&page_size=2", headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["total"] == 3
    assert len(res_data["items"]) == 2
    assert res_data["pages"] == 2


@pytest.mark.asyncio
async def test_get_dataset_preview(client: AsyncClient, db_session, test_user_db, test_project):
    headers = await get_auth_headers(client, "datasetfarmer@example.com")
    
    dataset = Dataset(
        id=uuid.uuid4(),
        project_id=test_project.id,
        user_id=test_user_db.id,
        name="preview_dataset",
        original_filename="preview.csv",
        stored_filename="stored_preview.csv",
        storage_path="path_preview.csv",
        status=DatasetStatus.VALIDATED,
        dataset_stage=DatasetStage.RAW,
        is_latest=True,
        delimiter=",",
        encoding="utf-8",
    )
    db_session.add(dataset)
    await db_session.flush()
    await db_session.commit()

    response = await client.get(f"/api/v1/datasets/{dataset.id}/preview", headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["dataset_id"] == str(dataset.id)
    assert res_data["columns"] == ["col1", "col2"]
    assert len(res_data["data"]) == 2


@pytest.mark.asyncio
async def test_rename_dataset(client: AsyncClient, db_session, test_user_db, test_project):
    headers = await get_auth_headers(client, "datasetfarmer@example.com")
    
    dataset = Dataset(
        id=uuid.uuid4(),
        project_id=test_project.id,
        user_id=test_user_db.id,
        name="old_name",
        original_filename="file.csv",
        stored_filename="stored.csv",
        storage_path="path.csv",
        status=DatasetStatus.VALIDATED,
        dataset_stage=DatasetStage.RAW,
        is_latest=True,
    )
    db_session.add(dataset)
    await db_session.flush()
    await db_session.commit()

    payload = {"name": "new_name", "description": "Updated desc", "tags": ["new_tag"]}
    response = await client.patch(f"/api/v1/datasets/{dataset.id}", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "new_name"
    assert response.json()["description"] == "Updated desc"
    assert "new_tag" in response.json()["tags"]


@pytest.mark.asyncio
async def test_delete_dataset_soft_delete(client: AsyncClient, db_session, test_user_db, test_project):
    headers = await get_auth_headers(client, "datasetfarmer@example.com")
    
    dataset = Dataset(
        id=uuid.uuid4(),
        project_id=test_project.id,
        user_id=test_user_db.id,
        name="to_delete",
        original_filename="file.csv",
        stored_filename="stored.csv",
        storage_path="path.csv",
        status=DatasetStatus.VALIDATED,
        dataset_stage=DatasetStage.RAW,
        is_latest=True,
    )
    db_session.add(dataset)
    await db_session.flush()
    await db_session.commit()

    response = await client.delete(f"/api/v1/datasets/{dataset.id}", headers=headers)
    assert response.status_code == 200
    
    from app.repositories.sqlalchemy.dataset import SqlAlchemyDatasetRepository
    repo = SqlAlchemyDatasetRepository(db_session)
    deleted_dataset = await repo.get_by_id_and_user_id(dataset.id, test_user_db.id)
    assert deleted_dataset is None

    await db_session.refresh(dataset)
    assert dataset.is_deleted is True
    assert dataset.is_latest is False
    assert dataset.deleted_at is not None


@pytest.mark.asyncio
async def test_delete_locked_dataset_fails(client: AsyncClient, db_session, test_user_db, test_project):
    headers = await get_auth_headers(client, "datasetfarmer@example.com")
    
    dataset = Dataset(
        id=uuid.uuid4(),
        project_id=test_project.id,
        user_id=test_user_db.id,
        name="locked_dataset",
        original_filename="file.csv",
        stored_filename="stored.csv",
        storage_path="path.csv",
        status=DatasetStatus.VALIDATED,
        dataset_stage=DatasetStage.RAW,
        is_latest=True,
        is_locked=True,
    )
    db_session.add(dataset)
    await db_session.flush()
    await db_session.commit()

    response = await client.delete(f"/api/v1/datasets/{dataset.id}", headers=headers)
    assert response.status_code == 409
    assert "locked" in response.json()["message"]
