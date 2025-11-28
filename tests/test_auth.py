import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "tier": "free"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data

@pytest.mark.anyio
async def test_register_existing_user(client: AsyncClient):
    # First registration
    await client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123"
        }
    )
    
    # Second registration (should fail)
    response = await client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered."

@pytest.mark.anyio
async def test_login_user(client: AsyncClient):
    # Register first
    await client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )
    
    # Login
    response = await client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.anyio
async def test_login_wrong_password(client: AsyncClient):
    # Register first
    await client.post(
        "/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "password123"
        }
    )
    
    # Login with wrong password
    response = await client.post(
        "/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
