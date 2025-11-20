"""
P0.6 - Happy Path End-to-End Tests
Tests du workflow complet de génération business brief
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.models.user import User
from app.core.quota import SubscriptionPlan

pytestmark = pytest.mark.asyncio


class TestBusinessBriefE2E:
    """
    Tests End-to-End pour le workflow complet Business Brief.
    
    Workflow validé:
    1. Vérification quota utilisateur (P0.5)
    2. Génération business brief via orchestrateur (mocké Sprint 1)
    3. Persistance Redis Virtual File System
    4. Incrémentation usage quota
    5. Récupération brief
    6. Validation données complètes
    """
    
    @patch('app.core.quota.quota_manager.QuotaManager.check_quota')
    @patch('app.core.quota.quota_manager.QuotaManager.increment_usage')
    @patch('app.core.orchestration.langgraph_orchestrator.LangGraphOrchestrator.run')
    @patch('app.core.integrations.redis_fs.RedisVirtualFileSystem.write_session')
    @patch('app.core.integrations.redis_fs.RedisVirtualFileSystem.read_session')
    async def test_happy_path_business_brief_generation(
        self,
        mock_redis_read,
        mock_redis_write,
        mock_orchestrator_run,
        mock_increment_usage,
        mock_check_quota,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """
        Test P0.6 - Happy path complet génération business brief.
        
        Scénario:
        1. Utilisateur Pro (quota OK : 30/50)
        2. Génération brief restaurant ivoirien
        3. Orchestrateur retourne résultats structurés
        4. Sauvegarde Redis réussie
        5. Usage incrémenté (31/50)
        6. Récupération brief validée
        7. Toutes les sections sub-agents présentes
        """
        
        # === 1. SETUP MOCKS ===
        
        # Mock quota check - utilisateur Pro avec quota disponible
        mock_check_quota.return_value = {
            "can_start_session": True,
            "current_usage": 30,
            "max_monthly_sessions": 50,
            "plan": SubscriptionPlan.PRO,
            "reset_date": "2025-12-01T00:00:00Z",
            "features_available": ["coaching", "business_brief", "market_research", "logo_generation", "seo_optimization"]
        }
        
        # Mock orchestrateur - résultats sub-agents
        mock_orchestrator_run.return_value = {
            "market_research": {
                "market_size": {
                    "estimated_value": "25M XOF",
                    "growth_rate": "15% annuel",
                    "market_segment": "Restauration moderne"
                },
                "competitors": [
                    {
                        "name": "Le Wafou",
                        "strengths": ["Cadre agréable", "Cuisine traditionnelle"],
                        "market_share": "20%"
                    },
                    {
                        "name": "Chez Georges",
                        "strengths": ["Prix abordables", "Localisation"],
                        "market_share": "15%"
                    }
                ],
                "opportunities": [
                    "Demande croissante cuisine fusion",
                    "Marché brunch weekend non saturé",
                    "Catering événementiel en expansion"
                ],
                "pricing_insights": {
                    "average_meal_price": "8,000 XOF",
                    "premium_segment": "12,000-18,000 XOF"
                }
            },
            "content_generation": {
                "homepage": {
                    "hero_title": "Redécouvrez la cuisine ivoirienne",
                    "hero_subtitle": "Fusion traditionnelle et moderne au cœur de Cocody",
                    "cta": "Réserver une table"
                },
                "about": {
                    "story": "Le Maquis Moderne réinvente l'expérience culinaire ivoirienne...",
                    "mission": "Proposer une cuisine africaine moderne et healthy",
                    "values": ["Qualité", "Innovation", "Authenticité"]
                },
                "services": [
                    {
                        "name": "Déjeuner d'affaires",
                        "description": "Menu exécutif 11h-15h",
                        "price": "8,500 XOF"
                    },
                    {
                        "name": "Brunch weekend",
                        "description": "Buffet brunch samedi-dimanche 10h-14h",
                        "price": "12,000 XOF"
                    }
                ],
                "seo_metadata": {
                    "title": "Le Maquis Moderne - Restaurant Fusion Africaine Abidjan",
                    "description": "Découvrez une cuisine ivoirienne moderne et healthy à Cocody. Déjeuner d'affaires, brunch weekend, catering événementiel.",
                    "keywords": ["restaurant abidjan", "cuisine ivoirienne", "fusion africaine", "cocody"]
                }
            },
            "logo_creation": {
                "primary_logo": {
                    "url": "https://mock-storage.genesis.ai/logos/maquis-moderne-primary.png",
                    "style": "modern-minimalist",
                    "format": "PNG"
                },
                "color_palette": [
                    {"name": "Orange Terre", "hex": "#E67E22"},
                    {"name": "Vert Forêt", "hex": "#27AE60"},
                    {"name": "Noir Profond", "hex": "#2C3E50"}
                ],
                "brand_guidelines": {
                    "fonts": ["Montserrat", "Lato"],
                    "tone": "Moderne, chaleureux, premium"
                }
            },
            "seo_optimization": {
                "primary_keywords": [
                    "restaurant abidjan cocody",
                    "cuisine ivoirienne moderne",
                    "brunch weekend abidjan"
                ],
                "local_seo_strategy": {
                    "google_my_business": "Optimisé pour 'Restaurant Cocody'",
                    "local_citations": ["Pages Jaunes CI", "Abidjan.net"],
                    "geo_targeting": "Cocody, Plateau, Marcory"
                },
                "meta_tags": {
                    "og:title": "Le Maquis Moderne - Restaurant Fusion Africaine",
                    "og:description": "Cuisine ivoirienne moderne à Cocody"
                }
            },
            "template_selection": {
                "primary_template": {
                    "name": "RestaurantPro Modern",
                    "preview_url": "https://templates.genesis.ai/restaurant-pro",
                    "features": ["Réservation en ligne", "Menu dynamique", "Galerie photos"]
                },
                "customizations": {
                    "header_style": "transparent-sticky",
                    "menu_layout": "grid-cards",
                    "contact_form": "integrated"
                }
            },
            "overall_confidence": 0.92,
            "is_ready_for_website": True
        }
        
        # Mock Redis write (capture les données sauvegardées)
        saved_data = {}
        async def mock_write(user_id, brief_id, data):
            saved_data['data'] = data
            saved_data['user_id'] = user_id
            saved_data['brief_id'] = brief_id
        mock_redis_write.side_effect = mock_write
        
        # Mock increment usage
        mock_increment_usage.return_value = {
            "new_usage": 31,
            "max_allowed": 50,
            "session_id": "brief_abc123"
        }
        
        # === 2. GÉNÉRATION BUSINESS BRIEF ===
        
        payload = {
            "user_id": test_user.id,
            "brief_data": {
                "business_name": "Le Maquis Moderne",
                "industry_sector": "Restauration",
                "vision": "Devenir le restaurant fusion africaine de référence à Abidjan",
                "mission": "Proposer une cuisine africaine moderne et healthy",
                "target_market": "Jeunes professionnels urbains 25-40 ans",
                "services": [
                    "Déjeuner d'affaires",
                    "Brunch weekend",
                    "Catering événementiel"
                ],
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
        
        # === 3. ASSERTIONS GÉNÉRATION ===
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        brief_data = response.json()
        brief_id = brief_data["brief_id"]
        
        # Vérifications structure réponse
        assert brief_id.startswith("brief_")
        assert brief_data["user_id"] == test_user.id
        assert brief_data["status"] == "completed"
        
        # Vérifications business_brief
        assert brief_data["business_brief"]["business_name"] == "Le Maquis Moderne"
        assert brief_data["business_brief"]["industry_sector"] == "Restauration"
        
        # Vérifications sub-agents results
        assert brief_data["market_research"]["status"] == "completed"
        assert brief_data["content_generation"]["status"] == "completed"
        assert brief_data["logo_creation"]["status"] == "completed"
        assert brief_data["seo_optimization"]["status"] == "completed"
        assert brief_data["template_selection"]["status"] == "completed"
        
        # Vérifications métriques
        assert brief_data["overall_confidence"] == 0.92
        assert brief_data["is_ready_for_website"] is True
        
        # Vérifications timestamps
        assert "created_at" in brief_data
        assert "updated_at" in brief_data
        
        # === 4. VÉRIFICATIONS MOCKS APPELÉS ===
        
        # Quota vérifié avant génération
        mock_check_quota.assert_called_once_with(test_user.id)
        
        # Orchestrateur exécuté
        mock_orchestrator_run.assert_called_once()
        orchestrator_input = mock_orchestrator_run.call_args[0][0]
        assert orchestrator_input["user_id"] == test_user.id
        assert orchestrator_input["brief_id"] == brief_id
        
        # Redis write appelé
        mock_redis_write.assert_called_once()
        assert saved_data['user_id'] == test_user.id
        assert saved_data['brief_id'] == brief_id
        
        # Usage incrémenté
        mock_increment_usage.assert_called_once_with(test_user.id, brief_id)
        
        # === 5. RÉCUPÉRATION BRIEF ===
        
        # Mock Redis read pour retourner les données sauvegardées
        mock_redis_read.return_value = saved_data['data']
        
        get_response = await client.get(
            f"/api/v1/genesis/business-brief/{brief_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        retrieved_brief = get_response.json()
        
        # === 6. ASSERTIONS RÉCUPÉRATION ===
        
        assert retrieved_brief["brief_id"] == brief_id
        assert retrieved_brief["business_brief"]["business_name"] == "Le Maquis Moderne"
        
        # Vérifier données market research détaillées
        market_research_data = retrieved_brief["market_research"]["data"]
        assert market_research_data["market_size"]["estimated_value"] == "25M XOF"
        assert len(market_research_data["competitors"]) == 2
        assert market_research_data["competitors"][0]["name"] == "Le Wafou"
        
        # Vérifier content generation
        content_data = retrieved_brief["content_generation"]["data"]
        assert content_data["homepage"]["hero_title"] == "Redécouvrez la cuisine ivoirienne"
        assert len(content_data["services"]) == 2
        
        # Vérifier logo creation
        logo_data = retrieved_brief["logo_creation"]["data"]
        assert logo_data["primary_logo"]["style"] == "modern-minimalist"
        assert len(logo_data["color_palette"]) == 3
        
        # Vérifier SEO
        seo_data = retrieved_brief["seo_optimization"]["data"]
        assert len(seo_data["primary_keywords"]) == 3
        assert "restaurant abidjan cocody" in seo_data["primary_keywords"]
        
        # Vérifier template
        template_data = retrieved_brief["template_selection"]["data"]
        assert template_data["primary_template"]["name"] == "RestaurantPro Modern"
        
        # === 7. VALIDATION WORKFLOW COMPLET ===
        
        # Le happy path E2E est validé si:
        # ✅ Quota vérifié (mock appelé)
        # ✅ Brief généré (201 Created)
        # ✅ Orchestrateur exécuté (mock appelé)
        # ✅ Redis sauvegarde (mock appelé)
        # ✅ Usage incrémenté (mock appelé)
        # ✅ Brief récupérable (200 OK)
        # ✅ Données complètes et cohérentes
        
        assert True  # Si on arrive ici, le happy path E2E est validé ✅
    
    
    @patch('app.core.quota.quota_manager.QuotaManager.check_quota')
    async def test_e2e_quota_exceeded_blocks_generation(
        self,
        mock_check_quota,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """
        Test E2E - Quota dépassé bloque génération.
        
        Valide que la vérification quota (P0.5) empêche bien
        la génération si quota dépassé.
        """
        from app.core.quota import QuotaExceededException
        
        # Mock quota dépassé
        mock_check_quota.side_effect = QuotaExceededException(
            message="Quota mensuel dépassé",
            current_usage=10,
            max_allowed=10,
            plan=SubscriptionPlan.BASIC,
            reset_date="2025-12-01T00:00:00Z"
        )
        
        payload = {
            "user_id": test_user.id,
            "brief_data": {
                "business_name": "Test Business",
                "industry_sector": "Test",
                "vision": "Test vision",
                "mission": "Test mission",
                "target_market": "Test market",
                "services": ["Test service"],
                "competitive_advantage": "Test advantage",
                "location": {"country": "CI", "city": "Abidjan"}
            }
        }
        
        response = await client.post(
            "/api/v1/genesis/business-brief/",
            json=payload,
            headers=auth_headers
        )
        
        # Doit retourner 403 Forbidden
        assert response.status_code == 403
        
        error_data = response.json()
        # FastAPI retourne les détails dans 'detail'
        details = error_data.get("detail", error_data)
        assert "current_usage" in details
        assert details["current_usage"] == 10
        assert details["max_allowed"] == 10
        assert details["plan"] == SubscriptionPlan.BASIC
        assert "upgrade_url" in details
    
    
    async def test_e2e_quota_status_endpoint(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """
        Test E2E - Endpoint statut quota pour frontend.
        
        Valide que le frontend peut récupérer le statut quota
        pour afficher barre progression.
        """
        with patch('app.core.quota.quota_manager.QuotaManager.get_quota_status') as mock_get_status:
            mock_get_status.return_value = {
                "user_id": test_user.id,
                "plan": SubscriptionPlan.PRO,
                "current_usage": 30,
                "max_monthly_sessions": 50,
                "remaining": 20,
                "reset_date": "2025-12-01T00:00:00Z",
                "percentage_used": 60.0
            }
            
            response = await client.get(
                "/api/v1/genesis/quota/status",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            
            quota_data = response.json()
            assert quota_data["plan"] == SubscriptionPlan.PRO
            assert quota_data["current_usage"] == 30
            assert quota_data["max_monthly_sessions"] == 50
            assert quota_data["remaining"] == 20
            assert quota_data["percentage_used"] == 60.0
"""
P0.6 - Happy Path End-to-End Tests
Tests du workflow complet de génération business brief
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.models.user import User
from app.core.quota import SubscriptionPlan

pytestmark = pytest.mark.asyncio


class TestBusinessBriefE2E:
    """
    Tests End-to-End pour le workflow complet Business Brief.
    
    Workflow validé:
    1. Vérification quota utilisateur (P0.5)
    2. Génération business brief via orchestrateur (mocké Sprint 1)
    3. Persistance Redis Virtual File System
    4. Incrémentation usage quota
    5. Récupération brief
    6. Validation données complètes
    """
    
    @patch('app.core.quota.quota_manager.QuotaManager.check_quota')
    @patch('app.core.quota.quota_manager.QuotaManager.increment_usage')
    @patch('app.core.orchestration.langgraph_orchestrator.LangGraphOrchestrator.run')
    @patch('app.core.integrations.redis_fs.RedisVirtualFileSystem.write_session')
    @patch('app.core.integrations.redis_fs.RedisVirtualFileSystem.read_session')
    async def test_happy_path_business_brief_generation(
        self,
        mock_redis_read,
        mock_redis_write,
        mock_orchestrator_run,
        mock_increment_usage,
        mock_check_quota,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """
        Test P0.6 - Happy path complet génération business brief.
        
        Scénario:
        1. Utilisateur Pro (quota OK : 30/50)
        2. Génération brief restaurant ivoirien
        3. Orchestrateur retourne résultats structurés
        4. Sauvegarde Redis réussie
        5. Usage incrémenté (31/50)
        6. Récupération brief validée
        7. Toutes les sections sub-agents présentes
        """
        
        # === 1. SETUP MOCKS ===
        
        # Mock quota check - utilisateur Pro avec quota disponible
        mock_check_quota.return_value = {
            "can_start_session": True,
            "current_usage": 30,
            "max_monthly_sessions": 50,
            "plan": SubscriptionPlan.PRO,
            "reset_date": "2025-12-01T00:00:00Z",
            "features_available": ["coaching", "business_brief", "market_research", "logo_generation", "seo_optimization"]
        }
        
        # Mock orchestrateur - résultats sub-agents
        mock_orchestrator_run.return_value = {
            "market_research": {
                "market_size": {
                    "estimated_value": "25M XOF",
                    "growth_rate": "15% annuel",
                    "market_segment": "Restauration moderne"
                },
                "competitors": [
                    {
                        "name": "Le Wafou",
                        "strengths": ["Cadre agréable", "Cuisine traditionnelle"],
                        "market_share": "20%"
                    },
                    {
                        "name": "Chez Georges",
                        "strengths": ["Prix abordables", "Localisation"],
                        "market_share": "15%"
                    }
                ],
                "opportunities": [
                    "Demande croissante cuisine fusion",
                    "Marché brunch weekend non saturé",
                    "Catering événementiel en expansion"
                ],
                "pricing_insights": {
                    "average_meal_price": "8,000 XOF",
                    "premium_segment": "12,000-18,000 XOF"
                }
            },
            "content_generation": {
                "homepage": {
                    "hero_title": "Redécouvrez la cuisine ivoirienne",
                    "hero_subtitle": "Fusion traditionnelle et moderne au cœur de Cocody",
                    "cta": "Réserver une table"
                },
                "about": {
                    "story": "Le Maquis Moderne réinvente l'expérience culinaire ivoirienne...",
                    "mission": "Proposer une cuisine africaine moderne et healthy",
                    "values": ["Qualité", "Innovation", "Authenticité"]
                },
                "services": [
                    {
                        "name": "Déjeuner d'affaires",
                        "description": "Menu exécutif 11h-15h",
                        "price": "8,500 XOF"
                    },
                    {
                        "name": "Brunch weekend",
                        "description": "Buffet brunch samedi-dimanche 10h-14h",
                        "price": "12,000 XOF"
                    }
                ],
                "seo_metadata": {
                    "title": "Le Maquis Moderne - Restaurant Fusion Africaine Abidjan",
                    "description": "Découvrez une cuisine ivoirienne moderne et healthy à Cocody. Déjeuner d'affaires, brunch weekend, catering événementiel.",
                    "keywords": ["restaurant abidjan", "cuisine ivoirienne", "fusion africaine", "cocody"]
                }
            },
            "logo_creation": {
                "primary_logo": {
                    "url": "https://mock-storage.genesis.ai/logos/maquis-moderne-primary.png",
                    "style": "modern-minimalist",
                    "format": "PNG"
                },
                "color_palette": [
                    {"name": "Orange Terre", "hex": "#E67E22"},
                    {"name": "Vert Forêt", "hex": "#27AE60"},
                    {"name": "Noir Profond", "hex": "#2C3E50"}
                ],
                "brand_guidelines": {
                    "fonts": ["Montserrat", "Lato"],
                    "tone": "Moderne, chaleureux, premium"
                }
            },
            "seo_optimization": {
                "primary_keywords": [
                    "restaurant abidjan cocody",
                    "cuisine ivoirienne moderne",
                    "brunch weekend abidjan"
                ],
                "local_seo_strategy": {
                    "google_my_business": "Optimisé pour 'Restaurant Cocody'",
                    "local_citations": ["Pages Jaunes CI", "Abidjan.net"],
                    "geo_targeting": "Cocody, Plateau, Marcory"
                },
                "meta_tags": {
                    "og:title": "Le Maquis Moderne - Restaurant Fusion Africaine",
                    "og:description": "Cuisine ivoirienne moderne à Cocody"
                }
            },
            "template_selection": {
                "primary_template": {
                    "name": "RestaurantPro Modern",
                    "preview_url": "https://templates.genesis.ai/restaurant-pro",
                    "features": ["Réservation en ligne", "Menu dynamique", "Galerie photos"]
                },
                "customizations": {
                    "header_style": "transparent-sticky",
                    "menu_layout": "grid-cards",
                    "contact_form": "integrated"
                }
            },
            "overall_confidence": 0.92,
            "is_ready_for_website": True
        }
        
        # Mock Redis write (capture les données sauvegardées)
        saved_data = {}
        async def mock_write(user_id, brief_id, data):
            saved_data['data'] = data
            saved_data['user_id'] = user_id
            saved_data['brief_id'] = brief_id
        mock_redis_write.side_effect = mock_write
        
        # Mock increment usage
        mock_increment_usage.return_value = {
            "new_usage": 31,
            "max_allowed": 50,
            "session_id": "brief_abc123"
        }
        
        # === 2. GÉNÉRATION BUSINESS BRIEF ===
        
        payload = {
            "user_id": test_user.id,
            "brief_data": {
                "business_name": "Le Maquis Moderne",
                "industry_sector": "Restauration",
                "vision": "Devenir le restaurant fusion africaine de référence à Abidjan",
                "mission": "Proposer une cuisine africaine moderne et healthy",
                "target_market": "Jeunes professionnels urbains 25-40 ans",
                "services": [
                    "Déjeuner d'affaires",
                    "Brunch weekend",
                    "Catering événementiel"
                ],
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
        
        # === 3. ASSERTIONS GÉNÉRATION ===
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        brief_data = response.json()
        brief_id = brief_data["brief_id"]
        
        # Vérifications structure réponse
        assert brief_id.startswith("brief_")
        assert brief_data["user_id"] == test_user.id
        assert brief_data["status"] == "completed"
        
        # Vérifications business_brief
        assert brief_data["business_brief"]["business_name"] == "Le Maquis Moderne"
        assert brief_data["business_brief"]["industry_sector"] == "Restauration"
        
        # Vérifications sub-agents results
        assert brief_data["market_research"]["status"] == "completed"
        assert brief_data["content_generation"]["status"] == "completed"
        assert brief_data["logo_creation"]["status"] == "completed"
        assert brief_data["seo_optimization"]["status"] == "completed"
        assert brief_data["template_selection"]["status"] == "completed"
        
        # Vérifications métriques
        assert brief_data["overall_confidence"] == 0.92
        assert brief_data["is_ready_for_website"] is True
        
        # Vérifications timestamps
        assert "created_at" in brief_data
        assert "updated_at" in brief_data
        
        # === 4. VÉRIFICATIONS MOCKS APPELÉS ===
        
        # Quota vérifié avant génération
        mock_check_quota.assert_called_once_with(test_user.id)
        
        # Orchestrateur exécuté
        mock_orchestrator_run.assert_called_once()
        orchestrator_input = mock_orchestrator_run.call_args[0][0]
        assert orchestrator_input["user_id"] == test_user.id
        assert orchestrator_input["brief_id"] == brief_id
        
        # Redis write appelé
        mock_redis_write.assert_called_once()
        assert saved_data['user_id'] == test_user.id
        assert saved_data['brief_id'] == brief_id
        
        # Usage incrémenté
        mock_increment_usage.assert_called_once_with(test_user.id, brief_id)
        
        # === 5. RÉCUPÉRATION BRIEF ===
        
        # Mock Redis read pour retourner les données sauvegardées
        mock_redis_read.return_value = saved_data['data']
        
        get_response = await client.get(
            f"/api/v1/genesis/business-brief/{brief_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        retrieved_brief = get_response.json()
        
        # === 6. ASSERTIONS RÉCUPÉRATION ===
        
        assert retrieved_brief["brief_id"] == brief_id
        assert retrieved_brief["business_brief"]["business_name"] == "Le Maquis Moderne"
        
        # Vérifier données market research détaillées
        market_research_data = retrieved_brief["market_research"]["data"]
        assert market_research_data["market_size"]["estimated_value"] == "25M XOF"
        assert len(market_research_data["competitors"]) == 2
        assert market_research_data["competitors"][0]["name"] == "Le Wafou"
        
        # Vérifier content generation
        content_data = retrieved_brief["content_generation"]["data"]
        assert content_data["homepage"]["hero_title"] == "Redécouvrez la cuisine ivoirienne"
        assert len(content_data["services"]) == 2
        
        # Vérifier logo creation
        logo_data = retrieved_brief["logo_creation"]["data"]
        assert logo_data["primary_logo"]["style"] == "modern-minimalist"
        assert len(logo_data["color_palette"]) == 3
        
        # Vérifier SEO
        seo_data = retrieved_brief["seo_optimization"]["data"]
        assert len(seo_data["primary_keywords"]) == 3
        assert "restaurant abidjan cocody" in seo_data["primary_keywords"]
        
        # Vérifier template
        template_data = retrieved_brief["template_selection"]["data"]
        assert template_data["primary_template"]["name"] == "RestaurantPro Modern"
        
        # === 7. VALIDATION WORKFLOW COMPLET ===
        
        # Le happy path E2E est validé si:
        # ✅ Quota vérifié (mock appelé)
        # ✅ Brief généré (201 Created)
        # ✅ Orchestrateur exécuté (mock appelé)
        # ✅ Redis sauvegarde (mock appelé)
        # ✅ Usage incrémenté (mock appelé)
        # ✅ Brief récupérable (200 OK)
        # ✅ Données complètes et cohérentes
        
        assert True  # Si on arrive ici, le happy path E2E est validé ✅
    
    
    @patch('app.core.quota.quota_manager.QuotaManager.check_quota')
    async def test_e2e_quota_exceeded_blocks_generation(
        self,
        mock_check_quota,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """
        Test E2E - Quota dépassé bloque génération.
        
        Valide que la vérification quota (P0.5) empêche bien
        la génération si quota dépassé.
        """
        from app.core.quota import QuotaExceededException
        
        # Mock quota dépassé
        mock_check_quota.side_effect = QuotaExceededException(
            message="Quota mensuel dépassé",
            current_usage=10,
            max_allowed=10,
            plan=SubscriptionPlan.BASIC,
            reset_date="2025-12-01T00:00:00Z"
        )
        
        payload = {
            "user_id": test_user.id,
            "brief_data": {
                "business_name": "Test Business",
                "industry_sector": "Test",
                "vision": "Test vision",
                "mission": "Test mission",
                "target_market": "Test market",
                "services": ["Test service"],
                "competitive_advantage": "Test advantage",
                "location": {"country": "CI", "city": "Abidjan"}
            }
        }
        
        response = await client.post(
            "/api/v1/genesis/business-brief/",
            json=payload,
            headers=auth_headers
        )
        
        # Doit retourner 403 Forbidden
        assert response.status_code == 403
        
        error_data = response.json()
        # FastAPI retourne les détails dans 'detail'
        details = error_data.get("detail", error_data)
        assert "current_usage" in details
        assert details["current_usage"] == 10
        assert details["max_allowed"] == 10
        assert details["plan"] == SubscriptionPlan.BASIC
        assert "upgrade_url" in details
    
    
    async def test_e2e_quota_status_endpoint(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """
        Test E2E - Endpoint statut quota pour frontend.
        
        Valide que le frontend peut récupérer le statut quota
        pour afficher barre progression.
        """
        with patch('app.core.quota.quota_manager.QuotaManager.get_quota_status') as mock_get_status:
            mock_get_status.return_value = {
                "user_id": test_user.id,
                "plan": SubscriptionPlan.PRO,
                "current_usage": 30,
                "max_monthly_sessions": 50,
                "remaining": 20,
                "reset_date": "2025-12-01T00:00:00Z",
                "percentage_used": 60.0
            }
            
            response = await client.get(
                "/api/v1/genesis/quota/status",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            
            quota_data = response.json()
            assert quota_data["plan"] == SubscriptionPlan.PRO
            assert quota_data["current_usage"] == 30
            assert quota_data["max_monthly_sessions"] == 50
            assert quota_data["remaining"] == 20
            assert quota_data["percentage_used"] == 60.0
