
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.core.integrations.redis_fs import RedisVirtualFileSystem

pytestmark = pytest.mark.asyncio

async def test_chat_site_generation_trigger(client: AsyncClient, auth_headers: dict):
    """
    Test that a message containing 'site' triggers the orchestrator
    and returns a site definition.
    """
    # Mock orchestrator response
    mock_state_result = {
        "user_id": 1,
        "brief_id": "test_brief_id",
        "business_brief": {
            "business_name": "Test Business",
            "industry_sector": "Tech",
            "mission": "Test Mission",
            "vision": "Test Vision",
            "services": ["Service 1", "Service 2"]
        },
        "market_research": {"some": "data"},
        "content_generation": {"some": "data"},
        "logo_creation": {"some": "data"},
        "seo_optimization": {"some": "data"},
        "template_selection": {"some": "data"},
        "overall_confidence": 0.9,
        "is_ready_for_website": True
    }

    # Mock Redis write
    mock_redis = AsyncMock(spec=RedisVirtualFileSystem)
    mock_redis.write_session.return_value = True

    # Mock Orchestrator
    mock_orchestrator = AsyncMock(spec=LangGraphOrchestrator)
    mock_orchestrator.run.return_value = mock_state_result

    # Override dependencies
    from app.main import app
    from app.api.v1.dependencies import get_orchestrator, get_redis_vfs

    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    app.dependency_overrides[get_redis_vfs] = lambda: mock_redis

    try:
        response = await client.post(
            "/api/v1/chat/",
            headers=auth_headers,
            json={"message": "Je veux créer un site pour mon business"}
        )

        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["brief_generated"] is True
        assert "site_data" in data
        assert data["site_data"]["metadata"]["title"] == "Test Business"
        
        # Verify new fields
        assert "orchestration_confidence" in data
        assert data["orchestration_confidence"] == 0.9
        assert "agents_status" in data
        assert data["agents_status"]["market_research"] == "success"
        
        # Verify orchestrator was called
        mock_orchestrator.run.assert_called_once()
        
        # Verify redis write
        mock_redis.write_session.assert_called_once()

    finally:
        app.dependency_overrides = {}

async def test_chat_normal_conversation(client: AsyncClient, auth_headers: dict):
    """
    Test that a normal message does NOT trigger the orchestrator.
    """
    mock_orchestrator = AsyncMock(spec=LangGraphOrchestrator)
    
    from app.main import app
    from app.api.v1.dependencies import get_orchestrator
    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator

    try:
        response = await client.post(
            "/api/v1/chat/",
            headers=auth_headers,
            json={"message": "Salut!"}  # Short message < 20 chars
        )

        assert response.status_code == 200
        data = response.json()
        
        assert data["brief_generated"] is False
        assert data["site_data"] is None
        
        # Verify orchestrator was NOT called
        mock_orchestrator.run.assert_not_called()

    finally:
        app.dependency_overrides = {}
