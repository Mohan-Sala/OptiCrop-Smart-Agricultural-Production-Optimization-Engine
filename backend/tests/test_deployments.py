import uuid
import pytest
import pytest_asyncio
import time
from datetime import datetime, time as dtime, timezone, timedelta
from httpx import AsyncClient
from cryptography.hazmat.primitives.asymmetric import ed25519
from sqlalchemy import delete

from app.models.project import Project
from app.models.dataset import Dataset
from app.models.training_session import TrainingSession
from app.models.trained_model import TrainedModel
from app.models.deployment import (
    DeploymentEnvironment,
    DeploymentSetting,
    DeploymentPolicy,
    ModelDeployment,
    DeploymentEvent,
    DeploymentApproval,
    DeploymentJobLock,
    DeploymentFreezeWindow,
)
from app.services.deployment.keys import SigningKeyRegistry
from app.services.deployment.checkpoints import CheckpointManager
from app.api.v1.routes.deployments import replay_timestamps, active_replays


async def get_auth_headers(client, email: str = "deploy_farmer@example.com", password: str = "SecurePassword123!") -> dict:
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Deploy Farmer",
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
    await get_auth_headers(client, "deploy_farmer@example.com")
    from app.repositories.sqlalchemy.user import SqlAlchemyUserRepository
    user_repo = SqlAlchemyUserRepository(db_session)
    user = await user_repo.get_by_email("deploy_farmer@example.com")
    return user


@pytest_asyncio.fixture
async def test_project(db_session, test_user_db):
    project = Project(
        id=uuid.uuid4(),
        user_id=test_user_db.id,
        name="Deploy Test Project",
        description="MLOps Platform Deployment",
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
        config_hash="confhash_dep",
    )
    db_session.add(session_record)
    await db_session.flush()

    model = TrainedModel(
        id=uuid.uuid4(),
        training_session_id=session_record.id,
        model_name="RandomForestClassifier_dep",
        algorithm="RandomForestClassifier",
        storage_path="models/rf_dep.joblib",
        version="1.0.0",
        is_active=True,
        status="READY",
        checksum="checksumrf_dep",
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


@pytest_asyncio.fixture
async def test_environment(db_session, test_project):
    env = DeploymentEnvironment(
        id=uuid.uuid4(),
        project_id=test_project.id,
        name="Production-Sagemaker",
        is_production=True,
        description="Primary production tier",
    )
    db_session.add(env)
    await db_session.flush()
    await db_session.commit()
    return env


@pytest_asyncio.fixture
async def test_policy(db_session, test_project):
    policy = DeploymentPolicy(
        id=uuid.uuid4(),
        project_id=test_project.id,
        name="Strict Enterprise Policy",
        required_approvals=2,
        minimum_health_checks=3,
        rollback_delay_seconds=60,
        promotion_stages={"stages": [10, 50, 100]},
        required_consecutive_successes=3,
        policy_version=1,
        is_active=True,
        policy_checksum="mockchecksum12345",
    )
    db_session.add(policy)
    await db_session.flush()
    await db_session.commit()
    return policy


# --- TESTS ---

@pytest.mark.asyncio
async def test_create_deployment_success(client: AsyncClient, test_project, test_model, test_environment, test_policy):
    headers = await get_auth_headers(client)
    payload = {
        "model_id": str(test_model.id),
        "environment_id": str(test_environment.id),
        "strategy": "CANARY",
        "deployment_version": "v1.0.0",
        "traffic_percentage": 0,
        "variables": [{"key": "DATABASE_URL", "value": "postgresql://db:5432/db", "required": True}],
        "tags": {"tier": "critical"}
    }
    response = await client.post(
        f"/api/v1/deployments/?project_id={test_project.id}",
        json=payload,
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "DRAFT"
    assert data["strategy"] == "CANARY"


@pytest.mark.asyncio
async def test_create_deployment_incompatible_strategy(client: AsyncClient, test_project, test_model, test_environment, test_policy):
    headers = await get_auth_headers(client)
    # Production-Sagemaker (environment) supports ROLLING, CANARY, BLUE_GREEN, SHADOW.
    # If environment is not production, LOCAL supports only ROLLING.
    # Let's create an environment with LOCAL provider (by setting is_production = False)
    # Then try to deploy with CANARY, which should raise incompatible strategy.
    
    # We will query /environments first to find/create a non-production one
    env_payload = {
        "name": "Staging-Local",
        "is_production": False,
        "description": "Local mock staging"
    }
    env_res = await client.post(
        f"/api/v1/deployments/environments?project_id={test_project.id}",
        json=env_payload,
        headers=headers
    )
    env_id = env_res.json()["id"]

    payload = {
        "model_id": str(test_model.id),
        "environment_id": env_id,
        "strategy": "CANARY", # Invalid for LOCAL (which only supports ROLLING)
        "deployment_version": "v1.0.0",
    }
    response = await client.post(
        f"/api/v1/deployments/?project_id={test_project.id}",
        json=payload,
        headers=headers
    )
    assert response.status_code == 400
    assert "strategy" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_create_deployment_blocked_by_freeze_window(client: AsyncClient, db_session, test_project, test_model, test_environment, test_policy):
    headers = await get_auth_headers(client)

    # Configure a freeze window spanning today/now
    now = datetime.now(timezone.utc)
    day_of_week = now.weekday()
    
    # Create freeze window covering the current day/time
    # E.g. start_day_of_week = day_of_week, start_time_utc = 00:00:00, end_day_of_week = day_of_week, end_time_utc = 23:59:59
    freeze_payload = {
        "name": "Emergency Freeze Window",
        "start_day_of_week": day_of_week,
        "start_time_utc": "00:00:00",
        "end_day_of_week": day_of_week,
        "end_time_utc": "23:59:59",
    }
    freeze_res = await client.post(
        f"/api/v1/deployments/freeze-windows?project_id={test_project.id}",
        json=freeze_payload,
        headers=headers
    )
    assert freeze_res.status_code == 201

    # Attempt to deploy: should fail with 403 Forbidden due to active freeze window
    payload = {
        "model_id": str(test_model.id),
        "environment_id": str(test_environment.id),
        "strategy": "ROLLING",
        "deployment_version": "v1.0.0",
    }
    response = await client.post(
        f"/api/v1/deployments/?project_id={test_project.id}",
        json=payload,
        headers=headers
    )
    assert response.status_code == 403
    assert "freeze window" in response.json()["message"].lower()

    # Clean up freeze window for other tests
    await db_session.execute(delete(DeploymentFreezeWindow))
    await db_session.commit()


@pytest.mark.asyncio
async def test_state_transitions_optimistic_locking(client: AsyncClient, db_session, test_project, test_model, test_environment, test_policy):
    headers = await get_auth_headers(client)
    
    # Create deployment
    payload = {
        "model_id": str(test_model.id),
        "environment_id": str(test_environment.id),
        "strategy": "ROLLING",
        "deployment_version": "v1.0.0",
    }
    res = await client.post(f"/api/v1/deployments/?project_id={test_project.id}", json=payload, headers=headers)
    deployment_id = res.json()["id"]

    # Try transition from DRAFT -> PENDING_APPROVAL with matching expected_state_version=1
    transition_res = await client.post(
        f"/api/v1/deployments/{deployment_id}/transition?next_state=PENDING_APPROVAL&expected_state_version=1",
        headers=headers
    )
    assert transition_res.status_code == 200
    assert transition_res.json()["status"] == "PENDING_APPROVAL"
    assert transition_res.json()["state_version"] == 2

    # Try transition from PENDING_APPROVAL -> APPROVED with mismatched expected_state_version=1 (stale lock/concurrency conflict)
    stale_res = await client.post(
        f"/api/v1/deployments/{deployment_id}/transition?next_state=APPROVED&expected_state_version=1",
        headers=headers
    )
    assert stale_res.status_code == 409 # Conflict
    assert "concurrency conflict" in stale_res.json()["message"].lower()


@pytest.mark.asyncio
async def test_approvals_eviction_and_promotion(client: AsyncClient, db_session, test_project, test_model, test_environment, test_policy):
    headers = await get_auth_headers(client)

    # 1. Create deployment
    payload = {
        "model_id": str(test_model.id),
        "environment_id": str(test_environment.id),
        "strategy": "ROLLING",
        "deployment_version": "v1.0.0",
    }
    res = await client.post(f"/api/v1/deployments/?project_id={test_project.id}", json=payload, headers=headers)
    dep_id = res.json()["id"]

    # Transition to PENDING_APPROVAL
    await client.post(
        f"/api/v1/deployments/{dep_id}/transition?next_state=PENDING_APPROVAL&expected_state_version=1",
        headers=headers
    )

    # Submit approval 1 (policy requires 2 approvals)
    app1 = await client.post(
        f"/api/v1/deployments/{dep_id}/approvals",
        json={"decision": "APPROVED", "comments": "First review looks good."},
        headers=headers
    )
    assert app1.status_code == 200
    # Status should still be PENDING_APPROVAL
    status_res1 = await client.get(f"/api/v1/deployments/{dep_id}", headers=headers)
    assert status_res1.json()["status"] == "PENDING_APPROVAL"

    # Submit approval 2 (should trigger automatic promotion to APPROVED status)
    app2 = await client.post(
        f"/api/v1/deployments/{dep_id}/approvals",
        json={"decision": "APPROVED", "comments": "Second review looks good."},
        headers=headers
    )
    assert app2.status_code == 200
    # Status should now be APPROVED
    status_res2 = await client.get(f"/api/v1/deployments/{dep_id}", headers=headers)
    assert status_res2.json()["status"] == "APPROVED"


@pytest.mark.asyncio
async def test_telemetry_cost_and_aggregates(client: AsyncClient, test_project, test_model, test_environment, test_policy):
    headers = await get_auth_headers(client)

    # Create a dummy deployment in DRAFT status
    payload = {
        "model_id": str(test_model.id),
        "environment_id": str(test_environment.id),
        "strategy": "ROLLING",
        "deployment_version": "v1.0.0",
    }
    res = await client.post(f"/api/v1/deployments/?project_id={test_project.id}", json=payload, headers=headers)
    dep_id = res.json()["id"]

    # Record health logs with resource utilization cost metrics
    health_payload = {
        "cpu_usage_pct": 45.5,
        "memory_usage_mb": 512.0,
        "latency_ms": 12.4,
        "throughput_rps": 120.0,
        "error_count": 2,
        "status": "HEALTHY",
        "deployment_duration_ms": 3000,
        "startup_time_ms": 1500,
        "container_ready_time": 2000,
        "traffic_shift_duration": 0,
        "rollback_duration": 0,
        "health_probe_count": 10,
        "successful_probe_count": 8,
        "failed_probe_count": 2,
        "estimated_cpu_cost": 0.05,
        "estimated_memory_cost": 0.02,
        "estimated_runtime_cost": 0.07,
        "estimated_network_cost": 0.01,
    }
    h_res = await client.post(
        f"/api/v1/deployments/{dep_id}/health-logs",
        json=health_payload,
        headers=headers
    )
    assert h_res.status_code == 200

    # Query aggregates
    agg_res = await client.get(
        f"/api/v1/deployments/{dep_id}/health-logs/aggregate",
        headers=headers
    )
    assert agg_res.status_code == 200
    agg_data = agg_res.json()
    assert agg_data["avg_cpu"] == 45.5
    assert agg_data["total_errors"] == 2


@pytest.mark.asyncio
async def test_replay_verification_rate_limiting(client: AsyncClient, test_project, test_model, test_environment, test_policy):
    import sys
    for name, module in list(sys.modules.items()):
        if "deployments" in name:
            if hasattr(module, "replay_timestamps"):
                getattr(module, "replay_timestamps").clear()
            if hasattr(module, "active_replays"):
                getattr(module, "active_replays").clear()
    headers = await get_auth_headers(client)

    payload = {
        "model_id": str(test_model.id),
        "environment_id": str(test_environment.id),
        "strategy": "ROLLING",
        "deployment_version": "v1.0.0",
    }
    res = await client.post(f"/api/v1/deployments/?project_id={test_project.id}", json=payload, headers=headers)
    dep_id = res.json()["id"]

    # Trigger replay rapidly to test rate limiting (max 20 per minute or parallel)
    # We trigger in a loop to see if HTTP 429 is encountered
    responses = []
    for _ in range(25):
        r = await client.post(f"/api/v1/deployments/{dep_id}/replay", headers=headers)
        responses.append(r.status_code)
    
    assert 429 in responses


@pytest.mark.asyncio
async def test_replay_verifications_diagnostics(client: AsyncClient, db_session, test_user_db, test_project, test_model, test_environment, test_policy):
    import sys
    for name, module in list(sys.modules.items()):
        if "deployments" in name:
            if hasattr(module, "replay_timestamps"):
                getattr(module, "replay_timestamps").clear()
            if hasattr(module, "active_replays"):
                getattr(module, "active_replays").clear()
    headers = await get_auth_headers(client)

    payload = {
        "model_id": str(test_model.id),
        "environment_id": str(test_environment.id),
        "strategy": "ROLLING",
        "deployment_version": "v1.0.0",
    }
    res = await client.post(f"/api/v1/deployments/?project_id={test_project.id}", json=payload, headers=headers)
    dep_id = res.json()["id"]

    # Seed some deployment events to replay
    event1 = DeploymentEvent(
        deployment_id=uuid.UUID(dep_id),
        event_id=uuid.uuid4(),
        correlation_id=uuid.uuid4(),
        trace_id=uuid.uuid4(),
        event_type="DeploymentInitiated",
        new_state="PROMOTING",
        sequence_number=1,
        current_event_hash="hash1",
    )
    event2 = DeploymentEvent(
        deployment_id=uuid.UUID(dep_id),
        event_id=uuid.uuid4(),
        correlation_id=uuid.uuid4(),
        trace_id=uuid.uuid4(),
        event_type="DeploymentSucceeded",
        new_state="PRODUCTION",
        sequence_number=2,
        current_event_hash="hash2",
    )
    db_session.add(event1)
    db_session.add(event2)

    # Seed settings
    settings_record = DeploymentSetting(
        project_id=test_project.id,
        checkpoint_interval=10,
        checkpoint_retention_days=30,
    )
    db_session.add(settings_record)
    await db_session.flush()
    await db_session.commit()

    # Trigger replay (no checkpoint case)
    replay_res = await client.post(f"/api/v1/deployments/{dep_id}/replay", headers=headers)
    assert replay_res.status_code == 200
    assert replay_res.json()["status"] == "FALLBACK_REPLAY"
    assert replay_res.json()["fallback_reason"] == "NO_CHECKPOINT"

    # Create key pair for digital signature validation
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes_raw()

    # Register in key registry
    SigningKeyRegistry.clear()
    SigningKeyRegistry.register_key("key-01", public_bytes, is_active=True)

    # Let's generate a valid checkpoint
    from app.repositories.sqlalchemy.deployment import SqlAlchemyDeploymentRepository
    repo = SqlAlchemyDeploymentRepository(db_session)
    checkpoint_mgr = CheckpointManager(repo)

    model_dep = await repo.get_deployment(uuid.UUID(dep_id))
    snapshot_data = b'{"state": "active", "active_nodes": 5}'

    # Generate and sign checkpoint
    checkpoint = await checkpoint_mgr.generate_checkpoint(
        deployment=model_dep,
        last_sequence_number=2,
        state_snapshot=snapshot_data,
        private_key=private_key,
        key_id="key-01",
        compression="GZIP"
    )
    await db_session.commit()

    # Trigger replay again (success case: should be FULLY_VERIFIED because sequence is contiguous up to 2 and no newer events)
    replay_res_2 = await client.post(f"/api/v1/deployments/{dep_id}/replay", headers=headers)
    assert replay_res_2.status_code == 200
    assert replay_res_2.json()["status"] == "FULLY_VERIFIED"
    assert replay_res_2.json()["verified_events"] == 0

    # Add a newer event with continuity gap (expected sequence 3, but we insert sequence 5)
    bad_event = DeploymentEvent(
        deployment_id=uuid.UUID(dep_id),
        event_id=uuid.uuid4(),
        correlation_id=uuid.uuid4(),
        trace_id=uuid.uuid4(),
        event_type="BadStateEvent",
        new_state="FAILED",
        sequence_number=5, # Gap from 2 to 5
        current_event_hash="hash3",
    )
    db_session.add(bad_event)
    await db_session.flush()
    await db_session.commit()

    # Trigger replay: should fallback with EVENT_SEQUENCE_GAP
    replay_res_3 = await client.post(f"/api/v1/deployments/{dep_id}/replay", headers=headers)
    assert replay_res_3.status_code == 200
    assert replay_res_3.json()["status"] == "FALLBACK_REPLAY"
    assert replay_res_3.json()["fallback_reason"] == "EVENT_SEQUENCE_GAP"
    assert replay_res_3.json()["failure_class"] == "EVENT_STREAM"

    # Revoke signing key and test revoked key failure
    SigningKeyRegistry.revoke_key("key-01")
    # Restore valid event continuity to isolate key test
    await db_session.execute(delete(DeploymentEvent).where(DeploymentEvent.sequence_number == 5))
    await db_session.commit()

    replay_res_4 = await client.post(f"/api/v1/deployments/{dep_id}/replay", headers=headers)
    assert replay_res_4.status_code == 200
    assert replay_res_4.json()["status"] == "FALLBACK_REPLAY"
    assert replay_res_4.json()["fallback_reason"] == "SIGNING_KEY_REVOKED"
    assert replay_res_4.json()["failure_class"] == "SECURITY"
