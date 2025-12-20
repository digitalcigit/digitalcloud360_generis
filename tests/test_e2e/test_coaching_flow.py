"""E2E Tests for the enhanced coaching flow (Vision to Site Generation)"""

import pytest
import json
import uuid
import asyncio
from httpx import AsyncClient
from app.models.user import User
from app.models.coaching import CoachingStepEnum

pytestmark = pytest.mark.asyncio

class TestCoachingFlowE2E:
    """End-to-end test suite for the coaching flow."""

    async def test_full_coaching_to_site_generation(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """ Tests a complete coaching journey for a fictional salon. """
        
        # 1. Start session
        start_response = await client.post(
            "/api/v1/coaching/start", 
            json={"message": "Je veux ouvrir un salon de coiffure moderne à Dakar."},
            headers=auth_headers
        )
        assert start_response.status_code == 200
        data = start_response.json()
        session_id = data["session_id"]
        assert data["current_step"] == CoachingStepEnum.VISION.value
        assert len(data["clickable_choices"]) > 0

        # Steps to complete (Simulating user responses with more detail for better LLM validation)
        steps = [
            (CoachingStepEnum.VISION, "Ma vision est de devenir le salon de référence pour la coiffure africaine moderne à Dakar, en valorisant la beauté naturelle de chaque femme."),
            (CoachingStepEnum.MISSION, "Ma mission est d'offrir des soins capillaires de haute qualité tout en préservant les traditions ancestrales et en utilisant des technologies modernes."),
            (CoachingStepEnum.CLIENTELE, "Je cible les femmes actives de Dakar, âgées de 25 à 45 ans, qui recherchent à la fois l'élégance, le respect de leurs racines et un service rapide."),
            (CoachingStepEnum.DIFFERENTIATION, "Nous nous différencions par l'utilisation exclusive de produits 100% locaux et bio, ainsi qu'une application de réservation qui réduit l'attente."),
            (CoachingStepEnum.OFFRE, "Nous proposons des tresses artistiques, des soins profonds aux huiles naturelles, et des manucures de luxe inspirées de l'art local.")
        ]

        for step_enum, response_text in steps:
            step_response = await client.post(
                "/api/v1/coaching/step",
                json={
                    "session_id": session_id,
                    "user_response": response_text
                },
                headers=auth_headers
            )
            assert step_response.status_code == 200
            step_data = step_response.json()
            
            # If it's not the last step, check transition
            if step_enum != CoachingStepEnum.OFFRE:
                assert step_data["is_step_complete"] is True
                assert step_data["current_step"] != step_enum.value
            else:
                # Last step (OFFRE) -> Check site generation
                assert step_data["is_step_complete"] is True
                assert step_data["site_data"] is not None
                
                # Adaptation structure GEN-8 (pages/sections)
                assert "pages" in step_data["site_data"]
                sections = step_data["site_data"]["pages"][0]["sections"]
                
                has_hero = any(b["type"] == "hero" for b in sections)
                has_about = any(b["type"] == "about" for b in sections)
                assert has_hero is True
                assert has_about is True

    async def test_coaching_validation_failure(self, client: AsyncClient, auth_headers: dict):
        """ Tests that insufficient responses block progression. """
        
        # Start session
        start_response = await client.post("/api/v1/coaching/start", json={}, headers=auth_headers)
        session_id = start_response.json()["session_id"]

        # Send a very short/vague response
        step_response = await client.post(
            "/api/v1/coaching/step",
            json={
                "session_id": session_id,
                "user_response": "Ok"
            },
            headers=auth_headers
        )
        assert step_response.status_code == 200
        data = step_response.json()
        
        # Should stay on VISION
        assert data["is_step_complete"] is False
        assert data["current_step"] == CoachingStepEnum.VISION.value
        assert any(word in data["coach_message"].lower() for word in ["préciser", "pouvez-vous", "pourriez-vous"])
