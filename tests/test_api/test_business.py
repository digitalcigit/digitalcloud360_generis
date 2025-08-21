"""Tests for business endpoints"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.models.user import User

pytestmark = pytest.mark.asyncio

# Mock data for testing
mock_brief_id = "brief_mock_123"
mock_session_id = "session_mock_123"

mock_request_data = {
    "session_id": mock_session_id,
    "business_needs": "Créer une plateforme de e-commerce pour la mode africaine.",
    "target_audience": "Jeunes adultes (18-35) intéressés par la mode durable.",
    "business_name": "AfroChic",
    "ton_of_voice": "Moderne, audacieux, et authentique.",
    "key_features": ["Catalogue de produits", "Paiement en ligne", "Blog de mode"]
}

mock_final_state = {
    "market_research": {"analysis": "Le marché est en pleine croissance..."},
    "content_generation": {"homepage_text": "Bienvenue chez AfroChic..."},
    "logo_creation": {"logo_url": "https://cdn.example.com/afrochic_logo.png"},
    "seo_optimization": {"keywords": ["mode africaine", "e-commerce", "durable"]},
    "template_selection": {"template_name": "DynamicFashion"}
}


@pytest.fixture
def mock_brief_data():
    """Mock business brief data for testing."""
    return {
        "brief_id": mock_brief_id,
        "user_id": None,  # This will be set within the tests
        "session_id": mock_session_id,
        "results": mock_final_state
    }


class TestBusinessEndpoints:
    """Test suite for the implemented business API endpoints."""

    async def test_generate_business_brief(self, client: AsyncClient, auth_headers: dict, test_user: User, mock_redis_vfs):
        """Test successful business brief generation."""
        response = await client.post("/api/v1/business/brief/generate", json=mock_request_data, headers=auth_headers)
        
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["user_id"] == test_user.id
        assert response_json["session_id"] == mock_session_id
        assert "results" in response_json
        mock_redis_vfs.write_session.assert_called_once()

    async def test_get_business_brief_found(self, client: AsyncClient, auth_headers: dict, mock_brief_data: dict, test_user: User, mock_redis_vfs):
        """Test retrieving an existing business brief."""
        mock_brief_data["user_id"] = test_user.id
        mock_redis_vfs.read_session.return_value = mock_brief_data
        
        response = await client.get(f"/api/v1/business/brief/{mock_brief_id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == mock_brief_data
        mock_redis_vfs.read_session.assert_called_once_with(test_user.id, mock_brief_id)

    async def test_get_business_brief_not_found(self, client: AsyncClient, auth_headers: dict, mock_redis_vfs):
        """Test retrieving a non-existent business brief."""
        mock_redis_vfs.read_session.return_value = None
        
        response = await client.get(f"/api/v1/business/brief/non_existent_id", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_subagent_results(self, client: AsyncClient, auth_headers: dict, mock_brief_data: dict, test_user: User, mock_redis_vfs):
        """Test retrieving sub-agent results for a brief."""
        mock_brief_data["user_id"] = test_user.id
        mock_redis_vfs.read_session.return_value = mock_brief_data

        response = await client.get(f"/api/v1/business/brief/{mock_brief_id}/results", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == mock_final_state

    async def test_regenerate_business_brief(self, client: AsyncClient, auth_headers: dict, mock_brief_data: dict, test_user: User, mock_redis_vfs, mock_orchestrator):
        """Test successful regeneration of specific brief sections."""
        mock_brief_data["user_id"] = test_user.id
        mock_redis_vfs.read_session.return_value = mock_brief_data
        mock_orchestrator.run.return_value = {"content_generation": {"homepage_text": "Nouveau texte de bienvenue..."}}

        response = await client.post(
            f"/api/v1/business/brief/{mock_brief_id}/regenerate",
            json={"sections": ["content_generation"]},
            headers=auth_headers
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["results"]["content_generation"]["homepage_text"] == "Nouveau texte de bienvenue..."
        assert response_json["results"]["market_research"] == mock_final_state["market_research"] # Ensure other sections are preserved
        mock_redis_vfs.write_session.assert_called_once()

    async def test_create_website_from_brief(self, client: AsyncClient, auth_headers: dict, mock_brief_data: dict, test_user: User, mock_redis_vfs, mock_digitalcloud360_client):
        """Test successful website creation from a brief."""
        mock_brief_data["user_id"] = test_user.id
        mock_redis_vfs.read_session.return_value = mock_brief_data

        response = await client.post(f"/api/v1/business/website/create?brief_id={mock_brief_id}", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["message"] == "Website creation initiated successfully."
        assert response.json()["website_id"] == "web_xyz"
        mock_digitalcloud360_client.create_website.assert_called_once_with(mock_brief_data)

    async def test_create_website_brief_not_found(self, client: AsyncClient, auth_headers: dict, mock_redis_vfs):
        """Test website creation when the brief is not found."""
        mock_redis_vfs.read_session.return_value = None

        response = await client.post(f"/api/v1/business/website/create?brief_id=non_existent_id", headers=auth_headers)

        assert response.status_code == 404

# TO BE EXPANDED BY DEVELOPMENT TEAM
# Ces tests doivent être complétés avec la vraie logique des sub-agents
@pytest.mark.skip(reason="To be implemented with actual sub-agents logic")
class TestSubAgentsOrchestration:
    """Tests for sub-agents orchestration workflow - TO IMPLEMENT"""
    
    async def test_research_subagent_market_analysis(self, mock_business_brief):
        """Test Research Sub-Agent avec Tavily API pour analyse marché"""
        pass
    
    async def test_content_subagent_multilingual_generation(self, mock_business_brief):
        """Test Content Sub-Agent génération multilingue"""
        pass
    
    async def test_logo_subagent_visual_identity(self, mock_business_brief):
        """Test Logo Sub-Agent création identité visuelle"""
        pass
    
    async def test_seo_subagent_local_optimization(self, mock_business_brief):
        """Test SEO Sub-Agent optimisation locale"""
        pass
    
    async def test_template_subagent_intelligent_selection(self, mock_business_brief):
        """Test Template Sub-Agent sélection intelligente"""
        pass
    
    async def test_parallel_subagents_execution(self, mock_business_brief):
        """Test exécution parallèle des 5 sub-agents"""
        pass
    
    async def test_business_brief_assembly(self, mock_business_brief):
        """Test assemblage du brief business final"""
        pass
    
    async def test_redis_virtual_filesystem_storage(self, mock_business_brief):
        """Test stockage dans Redis Virtual File System"""
        pass
    
    async def test_digitalcloud360_api_integration(self, mock_business_brief):
        """Test intégration API DigitalCloud360 pour création site"""
        pass
    
    async def test_subagents_performance_metrics(self, mock_business_brief):
        """Test métriques de performance des sub-agents"""
        pass
