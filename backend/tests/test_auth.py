"""
Authentication endpoint tests.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["username"] == "newuser"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    user_data = {
        "email": "dup@example.com",
        "username": "user1",
        "password": "SecurePass123!",
    }
    await client.post("/api/v1/auth/register", json=user_data)

    user_data["username"] = "user2"
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "short",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "SecurePass123!",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "loginuser",
            "password": "SecurePass123!",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "WrongPass123!",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile(authenticated_client):
    client, user = authenticated_client
    response = await client.get("/api/v1/auth/profile")
    assert response.status_code == 200
    assert response.json()["username"] == user["username"]


@pytest.mark.asyncio
async def test_profile_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/auth/profile")
    assert response.status_code == 403  # No auth header


@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient):
    # Register
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh@example.com",
            "username": "refreshuser",
            "password": "SecurePass123!",
        },
    )
    refresh_token = reg_response.json()["refresh_token"]

    # Refresh
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()