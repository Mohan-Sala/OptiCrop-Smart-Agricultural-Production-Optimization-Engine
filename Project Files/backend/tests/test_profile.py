import pytest
from fastapi import status


async def get_auth_headers(client, email: str = "testfarmer@example.com", password: str = "SecurePassword123!") -> dict:
    """Helper to authenticate a user session and return HTTP Headers."""
    # Attempt registration first to ensure the user profile exists for test isolation
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test Farmer",
    })
    payload = {"email": email, "password": password}
    response = await client.post("/api/v1/auth/login", json=payload)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_profile_unauthorized(client):
    """Verifies that requests to profile endpoints fail without JWT tokens."""
    response = await client.get("/api/v1/profile")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_profile_success(client):
    """Verifies that active authenticated sessions can read their profile properties."""
    headers = await get_auth_headers(client)
    response = await client.get("/api/v1/profile", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert json_data["email"] == "testfarmer@example.com"
    assert json_data["full_name"] == "Test Farmer"


@pytest.mark.asyncio
async def test_update_profile(client):
    """Verifies profile properties can be updated, excluding read-only fields."""
    headers = await get_auth_headers(client)
    payload = {
        "location": "Midwest Farms",
        "occupation": "Harvest Manager",
        "role": "Admin",  # Attempt to elevate role (Read-Only)
    }
    response = await client.put("/api/v1/profile", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert json_data["location"] == "Midwest Farms"
    assert json_data["occupation"] == "Harvest Manager"
    assert json_data["role"] == "Farmer"  # Enforces read-only protection of role


@pytest.mark.asyncio
async def test_change_password(client):
    """Verifies users can change their account passwords successfully."""
    headers = await get_auth_headers(client)
    payload = {
        "old_password": "SecurePassword123!",
        "new_password": "NewSecurePassword123!",
    }
    response = await client.post("/api/v1/profile/change-password", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert json_data["success"] is True

    # Confirm login succeeds with the new password
    login_payload = {
        "email": "testfarmer@example.com",
        "password": "NewSecurePassword123!",
    }
    login_response = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == status.HTTP_200_OK
