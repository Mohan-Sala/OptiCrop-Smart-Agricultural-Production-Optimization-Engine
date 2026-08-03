import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_register_user(client):
    """Verifies that user registration creates a new user profile successfully."""
    payload = {
        "email": "testfarmer@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test Farmer",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    json_data = response.json()
    assert json_data["email"] == "testfarmer@example.com"
    assert json_data["full_name"] == "Test Farmer"
    assert json_data["role"] == "Farmer"
    assert "id" in json_data


@pytest.mark.asyncio
async def test_register_user_duplicate_email(client):
    """Verifies that registering a duplicate email returns a conflict error."""
    payload = {
        "email": "testfarmer@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test Farmer Duplicate",
    }
    # First registration is created in the previous test (module-scoped DB persistence,
    # or client scope might clear, but since conftest uses standard db scope we can rely on it)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    json_data = response.json()
    assert json_data["success"] is False
    assert "already registered" in json_data["message"]


@pytest.mark.asyncio
async def test_login_user(client):
    """Verifies successful logins return access and refresh tokens."""
    payload = {
        "email": "testfarmer@example.com",
        "password": "SecurePassword123!",
        "device_name": "Web Browser",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert "access_token" in json_data
    assert "refresh_token" in json_data
    assert json_data["token_type"] == "bearer"
    assert json_data["user"]["email"] == "testfarmer@example.com"


@pytest.mark.asyncio
async def test_login_user_incorrect_credentials(client):
    """Verifies that logins with invalid credentials fail."""
    payload = {
        "email": "testfarmer@example.com",
        "password": "WrongPassword123!",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    json_data = response.json()
    assert json_data["success"] is False
    assert "Authentication failed" in json_data["message"]


@pytest.mark.asyncio
async def test_refresh_token(client):
    """Verifies that refresh token rotation returns fresh tokens."""
    # Obtain initial tokens
    login_payload = {
        "email": "testfarmer@example.com",
        "password": "SecurePassword123!",
    }
    login_response = await client.post("/api/v1/auth/login", json=login_payload)
    refresh_token = login_response.json()["refresh_token"]

    # Request rotation
    refresh_payload = {"refresh_token": refresh_token}
    refresh_response = await client.post("/api/v1/auth/refresh", json=refresh_payload)
    assert refresh_response.status_code == status.HTTP_200_OK

    json_data = refresh_response.json()
    assert "access_token" in json_data
    assert "refresh_token" in json_data
    assert json_data["refresh_token"] != refresh_token  # Enforces token rotation


@pytest.mark.asyncio
async def test_forgot_password(client):
    """Verifies password reset tokens can be successfully requested."""
    payload = {"email": "testfarmer@example.com"}
    response = await client.post("/api/v1/auth/forgot-password", json=payload)
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert json_data["success"] is True
    assert "reset_token" in json_data["data"]
