import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_read_root(client):
    """Verifies that the root landing endpoint returns a successful payload."""
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert json_data["success"] is True
    assert "data" in json_data
    assert json_data["data"]["environment"] == "testing"
    assert "timestamp" in json_data


@pytest.mark.asyncio
async def test_get_health(client):
    """Verifies that the health check API endpoint resolves and returns healthy status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "healthy"
    assert "timestamp" in json_data
    assert json_data["data"]["environment"] == "testing"

