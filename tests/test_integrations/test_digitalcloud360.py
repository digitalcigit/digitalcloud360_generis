"""Tests unitaires pour DigitalCloud360APIClient"""

import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch
from app.core.integrations.digitalcloud360 import DigitalCloud360APIClient


class TestDigitalCloud360APIClient:
    """Tests pour le client API DigitalCloud360"""
    
    @pytest.fixture
    def client(self):
        """Instance du client DigitalCloud360"""
        return DigitalCloud360APIClient()
    
    # Tests health_check
    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test health check réussi"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_instance.get.return_value = mock_response
            
            result = await client.health_check()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_api_error(self, client):
        """Test health check avec erreur API"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response = Mock()
            mock_response.status_code = 503
            mock_instance.get.return_value = mock_response
            
            result = await client.health_check()
            
            assert result is False
    
    # Tests get_user_profile
    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, client):
        """Test récupération profil utilisateur réussie"""
        user_id = 123
        expected_profile = {
            "id": user_id,
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_profile
            mock_instance.get.return_value = mock_response
            
            result = await client.get_user_profile(user_id)
            
            assert result == expected_profile
    
    # Tests create_website
    @pytest.mark.asyncio
    async def test_create_website_success(self, client):
        """Test création site web réussie"""
        business_brief = {
            "user_id": 123,
            "business_name": "Test Business"
        }
        
        expected_website = {
            "id": "website_456",
            "name": "Test Business",
            "status": "created"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = expected_website
            mock_instance.post.return_value = mock_response
            
            result = await client.create_website(business_brief)
            
            assert result["success"] is True
            assert result["website"] == expected_website
    
    # Tests configuration
    def test_client_initialization(self, client):
        """Test initialisation du client"""
        assert client.base_url is not None
        assert client.service_secret is not None
        assert "Content-Type" in client.headers
        assert "X-Service-Secret" in client.headers
        assert client.headers["Content-Type"] == "application/json"
