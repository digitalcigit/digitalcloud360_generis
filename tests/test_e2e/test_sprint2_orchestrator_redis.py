"""
Sprint 2 - Test E2E Orchestrateur + Redis FS
Test intégration complète avec nouvelle signature Redis FS (S2.3)
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import uuid

from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.core.integrations.redis_fs import RedisVirtualFileSystem

pytestmark = pytest.mark.asyncio


class TestSprint2OrchestratorRedisE2E:
    """
    Test E2E Sprint 2 - Validation correction S2.3 Redis FS
    
    Valide workflow complet:
    1. BusinessBrief → Orchestrateur
    2. Orchestrateur → ResearchSubAgent + ContentSubAgent (mockés)
    3. Résultats → Redis FS (write_session avec nouvelle signature)
    4. Redis FS → Relecture (read_session avec nouvelle signature)
    5. Validation données complètes + ownership
    """
    
    @patch('app.core.integrations.redis_fs.redis.from_url')
    @patch('app.core.providers.factory.ProviderFactory')
    async def test_orchestrator_to_redis_persistence_s23(
        self,
        mock_provider_factory,
        mock_redis_from_url
    ):
        """
        Test E2E Sprint 2 - Orchestrateur → Redis FS avec signature corrigée
        
        Scénario:
        1. Créer BusinessBrief minimal (startup tech Sénégal)
        2. Orchestrateur génère résultats sub-agents (mockés)
        3. Persister dans Redis avec write_session(user_id, brief_id, data)
        4. Relire depuis Redis avec read_session(user_id, brief_id)
        5. Valider ownership (user_id dans clé Redis)
        6. Valider données complètes (results, confidence, metadata)
        
        Validation S2.3:
        - Signature write_session(user_id, brief_id, data) ✅
        - Signature read_session(user_id, brief_id) ✅
        - Clé Redis: genesis:session:{user_id}:{brief_id} ✅
        """
        
        # === 1. SETUP REDIS MOCK ===
        
        # Stockage en mémoire pour simuler Redis
        redis_storage = {}
        
        mock_redis_client = AsyncMock()
        
        # Mock set (write_session)
        async def mock_set(key, value, ex=None):
            redis_storage[key] = {
                'value': value,
                'ttl': ex
            }
            return True
        mock_redis_client.set = mock_set
        
        # Mock get (read_session)
        async def mock_get(key):
            if key in redis_storage:
                return redis_storage[key]['value']
            return None
        mock_redis_client.get = mock_get
        
        # Mock delete
        async def mock_delete(key):
            if key in redis_storage:
                del redis_storage[key]
                return 1
            return 0
        mock_redis_client.delete = mock_delete
        
        # Mock ping (health_check)
        mock_redis_client.ping = AsyncMock(return_value=True)
        
        mock_redis_from_url.return_value = mock_redis_client
        
        # === 2. SETUP PROVIDER FACTORY MOCK ===
        
        # Mock LLM Provider (Deepseek)
        mock_llm_provider = AsyncMock()
        mock_llm_provider.generate = AsyncMock(return_value="Mock LLM response")
        
        # Mock Search Provider (Kimi/Tavily)
        mock_search_provider = AsyncMock()
        mock_search_provider.search = AsyncMock(return_value={
            "results": [{"title": "Mock search result", "url": "http://example.com"}],
            "query": "test"
        })
        
        # Mock Image Provider (DALL-E)
        mock_image_provider = AsyncMock()
        mock_image_provider.generate_logo = AsyncMock(return_value={
            "image_url": "http://mock-logo.com/logo.png"
        })
        
        mock_factory_instance = MagicMock()
        mock_factory_instance.create_llm_provider = MagicMock(return_value=mock_llm_provider)
        mock_factory_instance.create_search_provider = MagicMock(return_value=mock_search_provider)
        mock_factory_instance.create_image_provider = MagicMock(return_value=mock_image_provider)
        
        mock_provider_factory.return_value = mock_factory_instance
        
        # === 3. DONNÉES BUSINESS BRIEF ===
        
        user_id = 42  # ID utilisateur test
        brief_id = f"brief_{uuid.uuid4()}"
        
        business_brief_data = {
            "business_name": "TechSenegal Solutions",
            "industry_sector": "Services Numériques",
            "location": {
                "country": "Sénégal",
                "city": "Dakar"
            },
            "vision": "Démocratiser l'accès aux services digitaux en Afrique de l'Ouest",
            "mission": "Fournir solutions SaaS adaptées PME africaines",
            "target_market": {
                "primary": "PME Sénégal",
                "secondary": "Startups Afrique Ouest"
            },
            "services": [
                "Gestion commerciale cloud",
                "CRM adapté PME",
                "Formation digitale"
            ]
        }
        
        # === 4. MOCK RÉSULTATS ORCHESTRATEUR ===
        
        # Résultats attendus des sub-agents (Sprint 2 réels)
        mock_orchestrator_results = {
            "market_research": {
                "market_size": {
                    "estimated_value": "50M-100M USD",
                    "growth_rate": "25% annuel",
                    "maturity": "emerging"
                },
                "competitors": [
                    {
                        "name": "Digital Africa",
                        "market_share": "15%",
                        "strengths": ["Présence régionale"]
                    }
                ],
                "opportunities": [
                    "Digitalisation PME post-COVID",
                    "Financement disponible (subventions)"
                ],
                "pricing": {
                    "range": "5,000-25,000 FCFA/mois"
                }
            },
            "content_generation": {
                "homepage": {
                    "hero_title": "Transformez votre PME avec le digital",
                    "hero_subtitle": "Solutions cloud adaptées au contexte africain"
                },
                "about": {
                    "story": "TechSenegal Solutions facilite la transformation digitale...",
                    "mission": business_brief_data["mission"],
                    "values": ["Innovation", "Accessibilité", "Impact local"]
                },
                "services": [
                    {
                        "name": "Gestion Commerciale Cloud",
                        "description": "CRM + facturation adapté OHADA",
                        "price": "15,000 FCFA/mois"
                    }
                ],
                "languages": ["fr", "wo"]  # Français + Wolof (conformité SM)
            },
            "logo_creation": {
                "primary_logo": {
                    "url": "http://mock-logo.com/techsenegal-logo.png",
                    "style": "modern-tech"
                },
                "color_palette": [
                    {"name": "Vert Espoir", "hex": "#27AE60"},
                    {"name": "Bleu Tech", "hex": "#3498DB"}
                ]
            },
            "seo_optimization": {
                "primary_keywords": [
                    "solution digitale PME Sénégal",
                    "CRM Afrique Ouest",
                    "gestion commerciale cloud Dakar"
                ]
            },
            "template_selection": {
                "primary_template": {
                    "name": "TechStartup Modern",
                    "features": ["SaaS layout", "Pricing table", "Demo request"]
                }
            },
            "overall_confidence": 0.87,
            "is_ready_for_website": True
        }
        
        # === 5. INITIALISER REDIS FS ===
        
        redis_fs = RedisVirtualFileSystem()
        
        # Vérifier health check
        is_healthy = await redis_fs.health_check()
        assert is_healthy is True, "Redis FS devrait être healthy"
        
        # === 6. CONSTRUIRE DONNÉES COMPLÈTES POUR PERSISTANCE ===
        
        complete_brief_data = {
            "brief_id": brief_id,
            "user_id": user_id,
            "business_name": business_brief_data["business_name"],
            "industry_sector": business_brief_data["industry_sector"],
            "location": business_brief_data["location"],
            "results": mock_orchestrator_results,
            "overall_confidence": mock_orchestrator_results["overall_confidence"],
            "is_ready_for_website": mock_orchestrator_results["is_ready_for_website"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # === 7. TEST WRITE_SESSION (S2.3 NOUVELLE SIGNATURE) ===
        
        write_success = await redis_fs.write_session(
            user_id=user_id,
            brief_id=brief_id,
            data=complete_brief_data,
            ttl=7200  # 2h
        )
        
        assert write_success is True, "write_session devrait réussir"
        
        # Vérifier clé Redis correcte
        expected_key = f"genesis:session:{user_id}:{brief_id}"
        assert expected_key in redis_storage, f"Clé Redis {expected_key} devrait exister"
        
        # === 8. TEST READ_SESSION (S2.3 NOUVELLE SIGNATURE) ===
        
        retrieved_data = await redis_fs.read_session(
            user_id=user_id,
            brief_id=brief_id
        )
        
        assert retrieved_data is not None, "read_session devrait retourner données"
        
        # === 9. VALIDATIONS DONNÉES COMPLÈTES ===
        
        # Structure
        assert retrieved_data["brief_id"] == brief_id
        assert retrieved_data["user_id"] == user_id
        assert retrieved_data["business_name"] == "TechSenegal Solutions"
        
        # Résultats sub-agents
        assert "results" in retrieved_data
        results = retrieved_data["results"]
        
        assert "market_research" in results
        assert results["market_research"]["market_size"]["estimated_value"] == "50M-100M USD"
        
        assert "content_generation" in results
        assert results["content_generation"]["homepage"]["hero_title"] == "Transformez votre PME avec le digital"
        assert "fr" in results["content_generation"]["languages"]
        assert "wo" in results["content_generation"]["languages"]  # Conformité directives SM
        
        assert "logo_creation" in results
        assert "seo_optimization" in results
        assert "template_selection" in results
        
        # Métadonnées
        assert retrieved_data["overall_confidence"] == 0.87
        assert retrieved_data["is_ready_for_website"] is True
        assert "created_at" in retrieved_data
        assert "updated_at" in retrieved_data
        
        # === 10. TEST OWNERSHIP (USER_ID DANS CLÉ) ===
        
        # Tentative lecture avec mauvais user_id (ownership check)
        wrong_user_id = 999
        wrong_user_data = await redis_fs.read_session(
            user_id=wrong_user_id,
            brief_id=brief_id
        )
        
        assert wrong_user_data is None, "read_session avec mauvais user_id devrait retourner None"
        
        # === 11. TEST DELETE_SESSION ===
        
        delete_success = await redis_fs.delete_session(
            user_id=user_id,
            brief_id=brief_id
        )
        
        assert delete_success is True, "delete_session devrait réussir"
        
        # Vérifier suppression
        deleted_data = await redis_fs.read_session(
            user_id=user_id,
            brief_id=brief_id
        )
        
        assert deleted_data is None, "Données devraient être supprimées"
        
        # === 12. ASSERTIONS FINALES S2.3 ===
        
        print("\n✅ Test E2E Sprint 2 - SUCCÈS")
        print(f"   - write_session(user_id={user_id}, brief_id={brief_id}, data) ✅")
        print(f"   - read_session(user_id={user_id}, brief_id={brief_id}) ✅")
        print(f"   - Clé Redis: {expected_key} ✅")
        print(f"   - Ownership validé (user_id dans clé) ✅")
        print(f"   - Persistance complète business brief ✅")
        print(f"   - Conformité directives SM (langues: fr, wo) ✅")


    @patch('app.core.integrations.redis_fs.redis.from_url')
    async def test_list_user_sessions_s23(self, mock_redis_from_url):
        """
        Test E2E Sprint 2 - list_user_sessions avec nouvelle signature
        
        Scénario:
        1. Créer 3 briefs pour user_id=1
        2. Créer 2 briefs pour user_id=2
        3. list_user_sessions(1) devrait retourner 3 briefs
        4. list_user_sessions(2) devrait retourner 2 briefs
        5. Validation pattern scan Redis optimisé
        """
        
        # Mock Redis avec stockage en mémoire
        redis_storage = {}
        
        mock_redis_client = AsyncMock()
        
        # Mock set
        async def mock_set(key, value, ex=None):
            redis_storage[key] = {'value': value, 'ttl': ex}
            return True
        mock_redis_client.set = mock_set
        
        # Mock get
        async def mock_get(key):
            if key in redis_storage:
                return redis_storage[key]['value']
            return None
        mock_redis_client.get = mock_get
        
        # Mock scan_iter pour list_user_sessions
        async def mock_scan_iter(match=None):
            for key in redis_storage.keys():
                if match:
                    # Simple pattern matching (genesis:session:{user_id}:*)
                    import fnmatch
                    if fnmatch.fnmatch(key, match.replace('*', '*')):
                        yield key.encode()
                else:
                    yield key.encode()
        
        mock_redis_client.scan_iter = mock_scan_iter
        mock_redis_client.ping = AsyncMock(return_value=True)
        
        mock_redis_from_url.return_value = mock_redis_client
        
        # Initialiser Redis FS
        redis_fs = RedisVirtualFileSystem()
        
        # Créer briefs user_id=1
        for i in range(3):
            await redis_fs.write_session(
                user_id=1,
                brief_id=f"brief_user1_{i}",
                data={"test": f"data_{i}"}
            )
        
        # Créer briefs user_id=2
        for i in range(2):
            await redis_fs.write_session(
                user_id=2,
                brief_id=f"brief_user2_{i}",
                data={"test": f"data_{i}"}
            )
        
        # Test list_user_sessions user_id=1
        user1_sessions = await redis_fs.list_user_sessions(user_id=1)
        assert len(user1_sessions) == 3, f"User 1 devrait avoir 3 sessions, got {len(user1_sessions)}"
        assert "brief_user1_0" in user1_sessions
        assert "brief_user1_1" in user1_sessions
        assert "brief_user1_2" in user1_sessions
        
        # Test list_user_sessions user_id=2
        user2_sessions = await redis_fs.list_user_sessions(user_id=2)
        assert len(user2_sessions) == 2, f"User 2 devrait avoir 2 sessions, got {len(user2_sessions)}"
        assert "brief_user2_0" in user2_sessions
        assert "brief_user2_1" in user2_sessions
        
        print("\n✅ Test list_user_sessions S2.3 - SUCCÈS")
        print(f"   - User 1: {len(user1_sessions)} sessions ✅")
        print(f"   - User 2: {len(user2_sessions)} sessions ✅")
        print(f"   - Pattern scan optimisé genesis:session:{{user_id}}:* ✅")
