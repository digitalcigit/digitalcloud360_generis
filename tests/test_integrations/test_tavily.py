"""Tests unitaires pour TavilyClient"""

import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch
from app.core.integrations.tavily import TavilyClient


class TestTavilyClient:
    """Tests pour le client Tavily de recherche marché africain"""
    
    @pytest.fixture
    def client(self):
        """Instance du client Tavily"""
        return TavilyClient()
    
    # Tests health_check
    @pytest.mark.asyncio
    async def test_health_check_with_mock_key(self, client):
        """Test health check avec clé API mock (mode développement)"""
        with patch.object(client, 'api_key', 'your-tavily-key'):
            result = await client.health_check()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test health check réussi avec vraie API"""
        with patch.object(client, 'api_key', 'real-api-key'):
            with patch('httpx.AsyncClient') as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                
                mock_response = Mock()
                mock_response.status_code = 200
                mock_instance.post.return_value = mock_response
                
                result = await client.health_check()
                
                assert result is True
    
    # Tests search_market
    @pytest.mark.asyncio
    async def test_search_market_mock_mode(self, client):
        """Test recherche marché en mode mock"""
        with patch.object(client, 'api_key', 'your-tavily-key'):
            result = await client.search_market("agriculture", "Sénégal")
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert "agriculture" in result[0]["title"]
            assert "Sénégal" in result[0]["title"]
    
    @pytest.mark.asyncio
    async def test_search_market_success(self, client):
        """Test recherche marché réussie"""
        mock_response_data = {
            "results": [
                {
                    "title": "Market Analysis Africa",
                    "content": "Le marché africain présente des opportunités...",
                    "url": "https://example.com/market",
                    "score": 0.9
                }
            ]
        }
        
        with patch.object(client, 'api_key', 'real-api-key'):
            with patch('httpx.AsyncClient') as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = mock_response_data
                mock_instance.post.return_value = mock_response
                
                result = await client.search_market("agriculture", "Kenya")
                
                assert result == mock_response_data["results"]
    
    # Tests analyze_competitors
    @pytest.mark.asyncio
    async def test_analyze_competitors_mock_mode(self, client):
        """Test analyse concurrence en mode mock"""
        with patch.object(client, 'api_key', 'your-tavily-key'):
            result = await client.analyze_competitors("fintech", "Ghana")
            
            assert isinstance(result, dict)
            assert result["sector"] == "fintech"
            assert result["location"] == "Ghana"
            assert "competitors_found" in result
    
    # Tests research_trends
    @pytest.mark.asyncio
    async def test_research_trends_mock_mode(self, client):
        """Test recherche tendances en mode mock"""
        with patch.object(client, 'api_key', 'your-tavily-key'):
            result = await client.research_trends("agriculture", "Côte d'Ivoire")
            
            assert isinstance(result, dict)
            assert result["sector"] == "agriculture"
            assert result["location"] == "Côte d'Ivoire"
            assert "trends" in result
    
    # Tests des méthodes utilitaires
    def test_mock_market_search(self, client):
        """Test données mock pour recherche marché"""
        result = client._mock_market_search("agriculture", "Mali")
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert "agriculture" in result[0]["title"]
        assert "Mali" in result[0]["title"]
    
    def test_client_initialization(self, client):
        """Test initialisation du client"""
        assert client.api_key is not None
        assert client.base_url is not None
        assert "Content-Type" in client.headers
        assert "Authorization" in client.headers
        assert client.headers["Content-Type"] == "application/json"
    
    def test_get_timestamp(self, client):
        """Test génération timestamp"""
        timestamp = client._get_timestamp()
        
        assert isinstance(timestamp, str)
        assert "T" in timestamp  # Format ISO
