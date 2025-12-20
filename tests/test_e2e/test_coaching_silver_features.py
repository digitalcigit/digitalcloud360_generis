"""E2E Tests for Silver Level features (Help, Reformulate, Proposals)"""

import pytest
from httpx import AsyncClient
from app.models.user import User
from app.models.coaching import CoachingStepEnum

pytestmark = pytest.mark.asyncio

class TestSilverCoachingFeaturesE2E:
    """Tests for the proactive AI support features."""

    async def test_coaching_help_socratic(self, client: AsyncClient, auth_headers: dict):
        """Tests the assistance button (Socratic questions)."""
        
        # Start
        start_res = await client.post("/api/v1/coaching/start", json={}, headers=auth_headers)
        session_id = start_res.json()["session_id"]

        # Request help
        help_res = await client.post(
            "/api/v1/coaching/help",
            json={"session_id": session_id},
            headers=auth_headers
        )
        assert help_res.status_code == 200
        data = help_res.json()
        assert "socratic_questions" in data
        assert len(data["socratic_questions"]) >= 2
        assert "suggestion" in data

    async def test_reformulate_on_the_fly(self, client: AsyncClient, auth_headers: dict):
        """Tests real-time text reformulation."""
        
        long_text = "Je veux faire un truc de livraison de nourriture bio mais je sais pas trop comment dire ça proprement pour que ça fasse pro."
        
        response = await client.post(
            "/api/v1/coaching/reformulate",
            json={
                "session_id": "test-session-reformulate",
                "text": long_text,
                "target_step": "vision"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reformulated_text"] != long_text
        assert "livraison" in data["reformulated_text"].lower()

    async def test_reformulate_short_circuit(self, client: AsyncClient, auth_headers: dict):
        """Tests that short texts are not sent to LLM for reformulation (optimization)."""
        
        short_text = "C'est un resto."
        response = await client.post(
            "/api/v1/coaching/reformulate",
            json={
                "session_id": "test-session-short",
                "text": short_text
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reformulated_text"] == short_text
        assert data["is_better"] is False

    async def test_generate_proposals(self, client: AsyncClient, auth_headers: dict):
        """Tests the 'I don't know' mode generating 3 proposals."""
        
        # Start with a specific sector to ensure we have examples/proposals
        start_res = await client.post("/api/v1/coaching/start", json={}, headers=auth_headers)
        session_id = start_res.json()["session_id"]
        
        # Step with restaurant context to force sector detection
        await client.post(
            "/api/v1/coaching/step",
            json={"session_id": session_id, "user_response": "Ma vision est d'ouvrir un restaurant de spécialités ivoiriennes moderne et chic à Dakar pour faire découvrir la gastronomie de chez moi."},
            headers=auth_headers
        )

        # Get proposals
        prop_res = await client.post(
            "/api/v1/coaching/generate-proposals",
            json={"session_id": session_id},
            headers=auth_headers
        )
        assert prop_res.status_code == 200
        data = prop_res.json()
        assert len(data["proposals"]) == 3
        # Check for sector-relevant keywords
        keywords = ["restaurant", "cuisine", "plat", "alimentaire", "food", "ivoirien", "gastronomie", "délices", "saveurs", "menu"]
        assert any(word in p["content"].lower() for p in data["proposals"] for word in keywords)
