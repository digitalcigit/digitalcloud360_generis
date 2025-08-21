"""Tests for authentication endpoints"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User

pytestmark = pytest.mark.asyncio

# @pytest.fixture
# async def auth_headers(client: AsyncClient, test_user: User) -> dict:
#     """Fixture to get authentication headers for a test user."""
#     login_data = {
#         "username": test_user.email,
#         "password": "testpassword"
#     }
#     response = await client.post("/api/v1/auth/token", data=login_data)
#     token = response.json()["access_token"]
#     return {"Authorization": f"Bearer {token}"}

class TestAuthEndpoints:
    """Test suite for authentication API endpoints"""

    async def test_register_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful user registration."""
        user_data = {
            "email": "register_test@example.com",
            "name": "Test User",
            "password": "testpassword"
        }
        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        assert response.json()["email"] == user_data["email"]
        
        # Verify the user is in the database
        result = await db_session.execute(select(User).filter(User.email == "register_test@example.com"))
        user = result.scalar_one_or_none()
        assert user is not None

    # async def test_register_existing_user(self, client: AsyncClient, test_user: User):
    #     """Test registration with an existing email."""
    #     user_data = {
    #         "email": "test@example.com",
    #         "name": "Test User",
    #         "password": "testpassword"
    #     }
    #     response = await client.post("/api/v1/auth/register", json=user_data)
    #     assert response.status_code == 400

    # async def test_login_for_access_token(self, client: AsyncClient, test_user: User):
    #     """Test successful login and token generation."""
    #     login_data = {
    #         "username": "test@example.com",
    #         "password": "testpassword"
    #     }
    #     response = await client.post("/api/v1/auth/token", data=login_data)
    #     assert response.status_code == 200
    #     token = response.json()
    #     assert "access_token" in token
    #     assert token["token_type"] == "bearer"

    # async def test_login_incorrect_password(self, client: AsyncClient, test_user: User):
    #     """Test login with an incorrect password."""
    #     login_data = {
    #         "username": "test@example.com",
    #         "password": "wrongpassword"
    #     }
    #     response = await client.post("/api/v1/auth/token", data=login_data)
    #     assert response.status_code == 401

    # async def test_get_current_user(self, client: AsyncClient, auth_headers: dict, test_user: User):
    #     """Test retrieving the current user with a valid token."""
    #     response = await client.get(
    #         "/api/v1/auth/me",
    #         headers=auth_headers
    #     )
    #     assert response.status_code == 200
    #     user = response.json()
    #     assert user["email"] == test_user.email

    # async def test_get_current_user_invalid_token(self, client: AsyncClient):
    #     """Test retrieving the current user with an invalid token."""
    #     response = await client.get(
    #         "/api/v1/auth/me",
    #         headers={"Authorization": "Bearer invalidtoken"}
    #     )
    #     assert response.status_code == 401
