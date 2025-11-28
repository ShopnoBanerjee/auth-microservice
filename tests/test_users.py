import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_read_users_me(client: AsyncClient):
    # Register and login to get token
    await client.post(
        "/auth/register",
        json={
            "email": "me@example.com",
            "password": "password123"
        }
    )
    
    login_res = await client.post(
        "/auth/login",
        json={
            "email": "me@example.com",
            "password": "password123"
        }
    )
    token = login_res.json()["access_token"]
    
    # Get user profile
    response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"

@pytest.mark.anyio
async def test_read_users_me_unauthorized(client: AsyncClient):
    response = await client.get("/users/me")
    assert response.status_code == 401
