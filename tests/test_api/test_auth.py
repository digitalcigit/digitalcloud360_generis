"""Tests for authentication endpoints"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.schemas.user import UserCreate

class TestAuthEndpoints:
    """Test suite for authentication API endpoints"""
    
    def test_validate_token_unauthorized(self, client: TestClient):
        """Test that token validation returns 401 without valid token"""
        response = client.post(
            "/api/v1/auth/validate",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
        assert "Invalid authentication credentials" in response.json()["detail"]
    
    def test_get_user_profile_unauthorized(self, client: TestClient):
        """Test that user profile retrieval returns 401 without valid token"""
        response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
        assert "Invalid authentication credentials" in response.json()["detail"]
    
    def test_update_user_profile_unauthorized(self, client: TestClient):
        """Test that user profile update returns 401 without valid token"""
        profile_data = {
            "business_sector": "restaurant",
            "location": "Dakar",
            "language": "fr"
        }
        response = client.put(
            "/api/v1/auth/profile",
            json=profile_data,
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
        assert "Invalid authentication credentials" in response.json()["detail"]

@pytest.mark.asyncio
class TestAuthenticationFlow:
    """Tests for complete authentication workflow"""
    
    async def test_create_user_and_get_token(self, client: TestClient, db_session):
        """Test creating a user and getting a token"""
        # Create user
        user_data = {
            "email": "test@example.com",
            "password": "testpassword",
            "name": "Test User",
            "dc360_user_id": "12345"
        }
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 200
        user = response.json()
        assert user["email"] == user_data["email"]
        
        # Get token
        response = client.post("/api/v1/auth/token", json={"user_id": user["id"]})
        assert response.status_code == 200
        token = response.json()
        assert "access_token" in token
        assert token["token_type"] == "bearer"

    async def test_jwt_token_validation(self, client: TestClient):
        """Test JWT token validation"""
        # Get a token first
        response = client.post("/api/v1/auth/token", json={"user_id": 1})
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        # Validate the token
        response = client.post(
            "/api/v1/auth/validate",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        user = response.json()["user"]
        assert "email" in user
        assert "name" in user
    
    async def test_get_user_profile(self, client: TestClient):
        """Test getting user profile with valid token"""
        # Get a token first
        response = client.post("/api/v1/auth/token", json={"user_id": 1})
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        # Get the profile
        response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        profile = response.json()
        assert "email" in profile
        assert "name" in profile
