"""Tests pour l'endpoint business brief (generate & get)."""

import pytest
from datetime import datetime
from httpx import AsyncClient
from unittest.mock import AsyncMock

from app.main import app
from app.api.v1.dependencies import get_orchestrator, get_redis_vfs

pytestmark = pytest.mark.asyncio


@pytest.fixture
def brief_request_payload():
    """Payload conforme au schéma BusinessBriefRequest."""
    return {
        "coaching_session_id": 789,
        "session_id": "session_test_123",
        "business_brief": {
            "business_name": "TechStartup Dakar",
            "vision": "Devenir leader tech",
            "mission": "Démocratiser l'accès digital",
            "target_audience": "PME",
            "differentiation": "Support local",
            "value_proposition": "Solutions abordables",
            "sector": "Technology",
            "location": {"city": "Dakar", "country": "Senegal", "region": "West Africa"},
        },
    }


@pytest.fixture
def final_state():
    """État retourné par l'orchestrateur."""
    return {
        "market_research": {"analysis": "Croissance forte"},
        "content_generation": {"homepage_text": "Bienvenue"},
        "logo_creation": {"logo_url": "https://example.com/logo.png"},
        "seo_optimization": {"keywords": ["startup", "dakar"]},
        "template_selection": {"template_name": "Modern"},
        "overall_confidence": 0.75,
        "is_ready_for_website": True,
    }


@pytest.fixture
def mock_orchestrator(final_state):
    orch = AsyncMock()
    orch.run = AsyncMock(return_value=final_state)
    return orch


@pytest.fixture
def mock_redis_vfs():
    vfs = AsyncMock()
    vfs.write_session = AsyncMock(return_value=True)
    vfs.read_session = AsyncMock()
    return vfs


@pytest.fixture(autouse=True)
def override_dependencies(mock_orchestrator, mock_redis_vfs):
    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    app.dependency_overrides[get_redis_vfs] = lambda: mock_redis_vfs
    yield
    app.dependency_overrides.pop(get_orchestrator, None)
    app.dependency_overrides.pop(get_redis_vfs, None)


class TestBusinessBriefGenerate:
    async def test_generate_brief_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user,
        brief_request_payload,
        mock_redis_vfs,
        final_state,
    ):
        response = await client.post(
            "/api/v1/business/brief/generate",
            json=brief_request_payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()

        # Champs requis
        assert isinstance(data["id"], int)
        assert data["coaching_session_id"] == brief_request_payload["coaching_session_id"]
        assert data["business_brief"]["business_name"] == brief_request_payload["business_brief"]["business_name"]
        assert data["overall_confidence"] == final_state["overall_confidence"]
        assert data["is_ready_for_website"] is True

        # created_at présent et parsable
        datetime.fromisoformat(data["created_at"])

        mock_redis_vfs.write_session.assert_awaited_once()


class TestBusinessBriefGet:
    async def test_get_business_brief_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_redis_vfs,
        test_user,
        brief_request_payload,
    ):
        brief_id = 123
        stored_brief = {
            "id": brief_id,
            "coaching_session_id": brief_request_payload["coaching_session_id"],
            "business_brief": brief_request_payload["business_brief"],
            "market_research": {"analysis": "Croissance forte"},
            "overall_confidence": 0.8,
            "is_ready_for_website": False,
            "created_at": datetime.utcnow().isoformat(),
        }
        mock_redis_vfs.read_session.return_value = stored_brief

        response = await client.get(f"/api/v1/business/brief/{brief_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == brief_id
        assert data["business_brief"]["business_name"] == brief_request_payload["business_brief"]["business_name"]
        mock_redis_vfs.read_session.assert_awaited_once_with(test_user.id, str(brief_id))

    async def test_get_business_brief_not_found(self, client: AsyncClient, auth_headers: dict, mock_redis_vfs, test_user):
        mock_redis_vfs.read_session.return_value = None

        response = await client.get("/api/v1/business/brief/non_existent_id", headers=auth_headers)

        assert response.status_code == 404
