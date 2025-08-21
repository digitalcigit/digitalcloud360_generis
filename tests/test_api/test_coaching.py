"""Tests for coaching endpoints"""

import pytest
import json
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
import uuid
from app.models.user import User

pytestmark = pytest.mark.asyncio

# Mock data for testing
mock_session_id = str(uuid.uuid4())


@pytest.fixture
def mock_session_data():
    """Mock coaching session data for testing."""
    return {
        "user_id": None, # Will be set in the test
        "session_id": mock_session_id,
        "status": "initialized",
        "current_step": "vision",
        "id": 1  # Mock DB id
    }

class TestCoachingEndpoints:
    """Test suite for the implemented coaching API endpoints."""

    async def test_start_coaching_session(self, client: AsyncClient, auth_headers: dict, test_user: User, mock_redis_client):
        """Test successful start of a new coaching session."""
        mock_redis_client.get.return_value = None  # No existing session in Redis

        request_data = {
            "message": "Je veux créer un restaurant"
        }
        
        response = await client.post("/api/v1/coaching/start", json=request_data, headers=auth_headers)
        
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["current_step"] == "vision"
        assert "Bienvenue" in response_json["coach_message"]
        mock_redis_client.set.assert_called_once()

    async def test_process_coaching_step(self, client: AsyncClient, auth_headers: dict, mock_session_data: dict, test_user: User, mock_redis_client):
        """Test processing the 'vision' step and transitioning to 'mission'."""
        # Simulate an existing session in Redis
        mock_session_data["user_id"] = test_user.id
        mock_redis_client.get.return_value = json.dumps(mock_session_data)

        request_data = {
            "session_id": mock_session_id,
            "user_response": "Ma vision est de créer le meilleur restaurant de Dakar"
        }

        response = await client.post("/api/v1/coaching/step", json=request_data, headers=auth_headers)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["current_step"] == "mission"
        assert "MISSION" in response_json["coach_message"]
        assert response_json["progress"]["vision"] is True
        mock_redis_client.set.assert_called_once()

    async def test_get_coaching_session_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test that retrieving a non-existent session returns 404."""
        response = await client.get(f"/api/v1/coaching/session/{uuid.uuid4()}", headers=auth_headers)
        assert response.status_code == 404

    async def test_complete_coaching_session_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test that completing a non-existent session returns 404."""
        response = await client.post(f"/api/v1/coaching/complete?session_id={uuid.uuid4()}", headers=auth_headers)
        assert response.status_code == 404

    async def test_delete_coaching_session_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test that deleting a non-existent session returns 404."""
        response = await client.delete(f"/api/v1/coaching/session/{uuid.uuid4()}", headers=auth_headers)
        assert response.status_code == 404
