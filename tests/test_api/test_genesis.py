"""
Tests pour les endpoints Genesis alignés DC360
Route: /api/v1/genesis/business-brief/
"""

import pytest
from httpx import AsyncClient
from app.models.user import User

pytestmark = pytest.mark.asyncio


class TestGenesisBusinessBriefEndpoints:
    """Test suite pour endpoints Genesis Business Brief (P0.4)"""

    async def test_generate_business_brief_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_user: User
    ):
        """
        Test génération business brief avec payload aligné DC360.
        
        Valide:
        - Schéma request aligné avec wizard DC360
        - Réponse structurée avec sub-agents results
        - Status 201 Created
        """
        payload = {
            "user_id": test_user.id,
            "brief_data": {
                "business_name": "Restaurant Le Maquis Moderne",
                "industry_sector": "Restauration",
                "vision": "Devenir le restaurant fusion africaine de référence à Abidjan",
                "mission": "Proposer une cuisine africaine moderne et healthy",
                "target_market": "Jeunes professionnels urbains 25-40 ans",
                "services": ["Déjeuner d'affaires", "Brunch weekend", "Catering événementiel"],
                "competitive_advantage": "Fusion cuisine traditionnelle + techniques modernes",
                "location": {
                    "country": "Côte d'Ivoire",
                    "city": "Abidjan",
                    "region": "Cocody"
                },
                "years_in_business": 0,
                "differentiation": "Ingrédients locaux bio + présentation gastronomique",
                "value_proposition": "Redécouvrir la cuisine ivoirienne dans un cadre contemporain"
            }
        }
        
        response = await client.post(
            "/api/v1/genesis/business-brief/",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Validation structure réponse
        assert "brief_id" in data
        assert data["user_id"] == test_user.id
        assert data["status"] in ["completed", "in_progress"]
        
        # Validation business_brief
        assert data["business_brief"]["business_name"] == payload["brief_data"]["business_name"]
        assert data["business_brief"]["industry_sector"] == payload["brief_data"]["industry_sector"]
        
        # Validation sub-agents results (mockés Sprint 1)
        assert "market_research" in data
        assert "content_generation" in data
        assert "logo_creation" in data
        assert "seo_optimization" in data
        assert "template_selection" in data
        
        # Validation metadata
        assert "overall_confidence" in data
        assert "is_ready_for_website" in data
        assert "created_at" in data


    async def test_get_business_brief_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """
        Test récupération business brief existant.
        
        Valide:
        - GET /api/v1/genesis/business-brief/{brief_id}
        - Retour 200 avec données complètes
        """
        # 1. Générer un brief
        create_payload = {
            "user_id": test_user.id,
            "brief_data": {
                "business_name": "Boutique Wax & Style",
                "industry_sector": "Mode",
                "vision": "Rendre la mode africaine accessible",
                "mission": "Créer des vêtements modernes en wax",
                "target_market": "Femmes urbaines 18-35 ans",
                "services": ["Prêt-à-porter", "Sur-mesure"],
                "competitive_advantage": "Designs exclusifs + prix abordables",
                "location": {"country": "CI", "city": "Abidjan", "region": "Plateau"}
            }
        }
        
        create_response = await client.post(
            "/api/v1/genesis/business-brief/",
            json=create_payload,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        brief_id = create_response.json()["brief_id"]
        
        # 2. Récupérer le brief
        get_response = await client.get(
            f"/api/v1/genesis/business-brief/{brief_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        
        assert data["brief_id"] == brief_id
        assert data["business_brief"]["business_name"] == "Boutique Wax & Style"


    async def test_get_business_brief_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test récupération brief inexistant.
        
        Valide:
        - Retour 404 NOT FOUND
        - Message d'erreur structuré
        """
        response = await client.get(
            "/api/v1/genesis/business-brief/brief_nonexistent",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data


    async def test_delete_business_brief_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """
        Test suppression business brief.
        
        Valide:
        - DELETE /api/v1/genesis/business-brief/{brief_id}
        - Retour 204 NO CONTENT
        - Brief réellement supprimé
        """
        # 1. Créer un brief
        create_payload = {
            "user_id": test_user.id,
            "brief_data": {
                "business_name": "Test Brief to Delete",
                "industry_sector": "Test",
                "vision": "Test vision",
                "mission": "Test mission",
                "target_market": "Test market",
                "services": ["Test service"],
                "competitive_advantage": "Test advantage",
                "location": {"country": "CI", "city": "Abidjan"}
            }
        }
        
        create_response = await client.post(
            "/api/v1/genesis/business-brief/",
            json=create_payload,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        brief_id = create_response.json()["brief_id"]
        
        # 2. Supprimer le brief
        delete_response = await client.delete(
            f"/api/v1/genesis/business-brief/{brief_id}",
            headers=auth_headers
        )
        
        assert delete_response.status_code == 204
        
        # 3. Vérifier que le brief n'existe plus
        get_response = await client.get(
            f"/api/v1/genesis/business-brief/{brief_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


    async def test_generate_brief_missing_required_fields(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """
        Test génération avec champs requis manquants.
        
        Valide:
        - Retour 422 UNPROCESSABLE ENTITY
        - Validation Pydantic des champs requis
        """
        incomplete_payload = {
            "user_id": test_user.id,
            "brief_data": {
                "business_name": "Incomplete Business"
                # Manque: industry_sector, vision, mission, etc.
            }
        }
        
        response = await client.post(
            "/api/v1/genesis/business-brief/",
            json=incomplete_payload,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error


    async def test_generate_brief_unauthorized(self, client: AsyncClient):
        """
        Test génération sans authentification.
        
        Valide:
        - Retour 401 UNAUTHORIZED
        """
        payload = {
            "user_id": 999,
            "brief_data": {
                "business_name": "Test",
                "industry_sector": "Test",
                "vision": "Test",
                "mission": "Test",
                "target_market": "Test",
                "services": ["Test"],
                "competitive_advantage": "Test",
                "location": {"country": "CI", "city": "Abidjan"}
            }
        }
        
        response = await client.post(
            "/api/v1/genesis/business-brief/",
            json=payload
            # Pas de headers auth
        )
        
        assert response.status_code == 401
