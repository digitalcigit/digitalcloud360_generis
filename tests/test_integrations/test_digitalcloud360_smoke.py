"""
Sprint 2 - Tests smoke intégration DigitalCloud360
Validation connexion API DC360 (S2.4)
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.core.integrations.digitalcloud360 import DigitalCloud360APIClient
from app.config.settings import settings

pytestmark = pytest.mark.asyncio


class TestDigitalCloud360Integration:
    """Tests smoke intégration DigitalCloud360 API"""
    
    async def test_client_initialization(self):
        """Test initialisation client DC360"""
        client = DigitalCloud360APIClient()
        
        assert client.base_url == settings.DIGITALCLOUD360_API_URL
        assert client.service_secret == settings.DIGITALCLOUD360_SERVICE_SECRET
        assert client.timeout == settings.DIGITALCLOUD360_TIMEOUT
        assert "X-Service-Secret" in client.headers
        assert client.headers["Content-Type"] == "application/json"
    
    @patch('httpx.AsyncClient')
    async def test_health_check_success(self, mock_client_class):
        """Test health check DC360 - succès"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        
        mock_client_class.return_value = mock_client_instance
        
        # Test
        client = DigitalCloud360APIClient()
        is_healthy = await client.health_check()
        
        assert is_healthy is True
        mock_client_instance.get.assert_called_once()
    
    @patch('httpx.AsyncClient')
    async def test_health_check_failure(self, mock_client_class):
        """Test health check DC360 - échec"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 503
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        
        mock_client_class.return_value = mock_client_instance
        
        # Test
        client = DigitalCloud360APIClient()
        is_healthy = await client.health_check()
        
        assert is_healthy is False
    
    @patch('httpx.AsyncClient')
    async def test_get_user_subscription_success(self, mock_client_class):
        """Test récupération subscription utilisateur - succès"""
        # Mock subscription data
        subscription_data = {
            "plan": "pro",
            "genesis_sessions_used": 15,
            "quota_reset_date": "2025-12-01T00:00:00Z",
            "subscription_status": "active",
            "max_monthly_sessions": 50
        }
        
        mock_response = AsyncMock()
        mock_response.status_code = 200
        # json() doit retourner directement le dict (pas async)
        mock_response.json = lambda: subscription_data
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        
        mock_client_class.return_value = mock_client_instance
        
        # Test
        client = DigitalCloud360APIClient()
        result = await client.get_user_subscription(user_id=42)
        
        assert result is not None
        assert result["plan"] == "pro"
        assert result["genesis_sessions_used"] == 15
        assert result["max_monthly_sessions"] == 50
        assert result["subscription_status"] == "active"
    
    @patch('httpx.AsyncClient')
    async def test_create_website_success(self, mock_client_class):
        """Test création site web via DC360 - succès"""
        # Mock business brief
        business_brief = {
            "user_id": 42,
            "business_name": "TechSenegal",
            "industry_sector": "Services Numériques",
            "results": {
                "homepage": {"hero_title": "Bienvenue"}
            }
        }
        
        # Mock website response
        website_data = {
            "id": "website_123",
            "user_id": 42,
            "status": "created",
            "url": "https://techsenegal.digitalcloud360.com"
        }
        
        mock_response = AsyncMock()
        mock_response.status_code = 201
        mock_response.json = lambda: website_data
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        
        mock_client_class.return_value = mock_client_instance
        
        # Test
        client = DigitalCloud360APIClient()
        result = await client.create_website(business_brief)
        
        assert result["success"] is True
        assert result["website"]["id"] == "website_123"
        assert result["website"]["status"] == "created"
    
    @patch('httpx.AsyncClient')
    async def test_create_website_failure(self, mock_client_class):
        """Test création site web via DC360 - échec"""
        business_brief = {"user_id": 42}
        
        # Mock error response
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid business brief format"
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        
        mock_client_class.return_value = mock_client_instance
        
        # Test
        client = DigitalCloud360APIClient()
        result = await client.create_website(business_brief)
        
        assert result["success"] is False
        assert "API returned status 400" in result["error"]
    
    async def test_fallback_mode_configuration(self):
        """Test configuration fallback mode DC360"""
        # Vérifier que settings contient les configs nécessaires
        assert hasattr(settings, 'DIGITALCLOUD360_API_URL')
        assert hasattr(settings, 'DIGITALCLOUD360_SERVICE_SECRET')
        assert hasattr(settings, 'DIGITALCLOUD360_TIMEOUT')
        
        # En mode fallback, l'URL peut être une URL de test/mock
        # ou le service fonctionne sans DC360 réel
        client = DigitalCloud360APIClient()
        assert client.base_url is not None
        
        print(f"\n✅ DC360 Configuration:")
        print(f"   - Base URL: {client.base_url}")
        print(f"   - Timeout: {client.timeout}s")
        print(f"   - Fallback mode: {'ENABLED' if 'test' in client.base_url.lower() or 'mock' in client.base_url.lower() else 'DISABLED'}")
