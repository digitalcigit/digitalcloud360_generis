"""
Tests pour l'adaptateur DC360
Tests du WO-GENESIS-DC360-ADAPTER-S3-001
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.dc360_adapter import adapt_dc360_to_genesis, DC360GenerateBriefRequest, DC360BusinessInfo, DC360MarketInfo
from app.config.settings import settings


class TestDC360PayloadAdapter:
    """Tests de la fonction d'adaptation payload DC360 → Genesis"""
    
    def test_adapt_dc360_to_genesis_basic(self):
        """Vérifie la transformation du payload DC360 → Genesis"""
        # Arrange
        dc360_request = DC360GenerateBriefRequest(
            user_id=123,
            business_info=DC360BusinessInfo(
                company_name="Test Corp",
                industry="Tech",
                company_size="1-10",
                description="Test description entreprise innovante"
            ),
            market_info=DC360MarketInfo(
                target_audience="PME et startups",
                competitors=["Concurrent A", "Concurrent B"],
                market_challenges="Financement, visibilité",
                goals=["Augmenter CA", "Expansion"]
            )
        )
        
        # Act
        genesis_payload = adapt_dc360_to_genesis(dc360_request)
        
        # Assert
        assert genesis_payload["user_id"] == 123
        assert genesis_payload["brief_data"]["business_name"] == "Test Corp"
        assert genesis_payload["brief_data"]["industry_sector"] == "Tech"
        assert genesis_payload["brief_data"]["vision"] == "Test description entreprise innovante"
        assert genesis_payload["brief_data"]["mission"] == "Test description entreprise innovante"
        assert genesis_payload["brief_data"]["target_market"] == "PME et startups"
        assert genesis_payload["brief_data"]["competitive_advantage"] == "Concurrent A, Concurrent B"
        assert genesis_payload["brief_data"]["services"] == ["Augmenter CA", "Expansion"]
        assert "session_" in genesis_payload.get("coaching_session_id", "")
    
    def test_adapt_dc360_location_default(self):
        """Vérifie que la localisation par défaut est Dakar, Sénégal"""
        dc360_request = DC360GenerateBriefRequest(
            user_id=456,
            business_info=DC360BusinessInfo(
                company_name="Startup Dakar",
                industry="Tech",
                description="Startup tech"
            ),
            market_info=DC360MarketInfo(
                target_audience="Entrepreneurs",
                goals=["Croissance"]
            )
        )
        
        genesis_payload = adapt_dc360_to_genesis(dc360_request)
        
        assert genesis_payload["brief_data"]["location"]["country"] == "Sénégal"
        assert genesis_payload["brief_data"]["location"]["city"] == "Dakar"
        assert genesis_payload["brief_data"]["location"]["region"] == "Afrique de l'Ouest"
    
    def test_adapt_dc360_empty_competitors(self):
        """Vérifie le comportement avec liste concurrents vide"""
        dc360_request = DC360GenerateBriefRequest(
            user_id=789,
            business_info=DC360BusinessInfo(
                company_name="New Business",
                industry="Consulting",
                description="Nouveau business"
            ),
            market_info=DC360MarketInfo(
                target_audience="PME",
                competitors=[],  # Liste vide
                goals=["Innovation"]
            )
        )
        
        genesis_payload = adapt_dc360_to_genesis(dc360_request)
        
        assert genesis_payload["brief_data"]["competitive_advantage"] == "À définir"
    
    def test_coaching_session_id_generated(self):
        """Vérifie que coaching_session_id est auto-généré"""
        dc360_request = DC360GenerateBriefRequest(
            user_id=999,
            business_info=DC360BusinessInfo(
                company_name="Test",
                industry="Services",
                description="Test"
            ),
            market_info=DC360MarketInfo(
                target_audience="Test",
                goals=["Test"]
            )
        )
        
        genesis_payload = adapt_dc360_to_genesis(dc360_request)
        
        session_id = genesis_payload.get("coaching_session_id", "")
        assert session_id.startswith("session_")
        assert len(session_id) > 8  # session_ + 8 chars hex


class TestDC360AdapterEndpoint:
    """Tests de l'endpoint /api/genesis/generate-brief/"""
    
    @pytest.mark.asyncio
    async def test_generate_brief_missing_service_secret(self):
        """Test refus sans X-Service-Secret"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "user_id": 123,
                "business_info": {
                    "company_name": "Test",
                    "industry": "Tech",
                    "description": "Test"
                },
                "market_info": {
                    "target_audience": "PME",
                    "goals": ["Test"]
                }
            }
            
            response = await client.post(
                "/api/genesis/generate-brief/",
                json=payload
                # Pas de header X-Service-Secret
            )
            
            assert response.status_code == 422  # Validation error (header manquant)
    
    @pytest.mark.asyncio
    async def test_generate_brief_invalid_service_secret(self):
        """Test refus avec X-Service-Secret invalide"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "user_id": 123,
                "business_info": {
                    "company_name": "Test",
                    "industry": "Tech",
                    "description": "Test"
                },
                "market_info": {
                    "target_audience": "PME",
                    "goals": ["Test"]
                }
            }
            
            response = await client.post(
                "/api/genesis/generate-brief/",
                json=payload,
                headers={"X-Service-Secret": "invalid_secret_123"}
            )
            
            assert response.status_code == 401
            data = response.json()
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_generate_brief_invalid_payload(self):
        """Test refus avec payload invalide"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Payload incomplet (manque business_info)
            payload = {
                "user_id": 123,
                "market_info": {
                    "target_audience": "PME"
                }
            }
            
            response = await client.post(
                "/api/genesis/generate-brief/",
                json=payload,
                headers={"X-Service-Secret": settings.GENESIS_SERVICE_SECRET}
            )
            
            assert response.status_code == 422  # Validation Pydantic échoue
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_brief_success_mock(self, monkeypatch):
        """Test génération brief avec mocks (succès)"""
        # Mock orchestrator
        class MockOrchestrator:
            async def run(self, input_data):
                return {
                    "market_research": {"competitors_found": 3},
                    "content_generation": {"pages_generated": 5},
                    "logo_creation": {"url": "https://example.com/logo.png"},
                    "seo_optimization": {"keywords": 10},
                    "template_selection": {"template_id": "modern_01"},
                    "confidence_score": 0.85,
                    "ready_for_website": True
                }
        
        # Mock Redis VFS
        class MockRedisVFS:
            async def write_session(self, user_id, brief_id, data, ttl):
                return True
        
        # Mock Quota Manager
        class MockQuotaManager:
            async def check_quota(self, user_id):
                return {
                    "plan": "genesis_pro",
                    "current_usage": 10,
                    "max_monthly_sessions": 50
                }
            
            async def increment_usage(self, user_id):
                return True
        
        # Apply mocks
        from app.api import dc360_adapter
        monkeypatch.setattr(dc360_adapter, "get_orchestrator", lambda: MockOrchestrator())
        monkeypatch.setattr(dc360_adapter, "get_redis_vfs", lambda: MockRedisVFS())
        monkeypatch.setattr(dc360_adapter, "get_quota_manager", lambda: MockQuotaManager())
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "user_id": 123,
                "business_info": {
                    "company_name": "TechHub Dakar",
                    "industry": "Technology",
                    "company_size": "1-10",
                    "description": "Startup tech innovante au Sénégal"
                },
                "market_info": {
                    "target_audience": "PME et entrepreneurs",
                    "competitors": ["Jokkolabs", "Teranga Tech"],
                    "market_challenges": "Accès financement",
                    "goals": ["Augmenter visibilité", "Générer leads"]
                }
            }
            
            response = await client.post(
                "/api/genesis/generate-brief/",
                json=payload,
                headers={"X-Service-Secret": settings.GENESIS_SERVICE_SECRET}
            )
            
            assert response.status_code == 201
            data = response.json()
            
            # Vérifications response structure
            assert "id" in data
            assert data["id"].startswith("brief_")
            assert data["user_id"] == 123
            assert data["status"] == "completed"
            assert "session_id" in data
            assert data["session_id"].startswith("session_")
            
            # Vérifications sub-agents results
            assert data["market_research"]["status"] == "completed"
            assert data["content_generation"]["status"] == "completed"
            assert data["template_selection"]["status"] == "completed"
            
            # Vérifications metadata
            assert data["overall_confidence"] == 0.85
            assert data["is_ready_for_website"] is True
            assert "generated_at" in data


class TestDC360AdapterServiceSecret:
    """Tests spécifiques à la validation du service secret"""
    
    @pytest.mark.asyncio
    async def test_verify_service_secret_valid(self):
        """Test validation service secret valide"""
        from app.api.dc360_adapter import verify_service_secret
        
        result = await verify_service_secret(x_service_secret=settings.GENESIS_SERVICE_SECRET)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_service_secret_invalid_raises_401(self):
        """Test validation service secret invalide lève 401"""
        from app.api.dc360_adapter import verify_service_secret
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            await verify_service_secret(x_service_secret="wrong_secret")
        
        assert exc_info.value.status_code == 401
        assert "Invalid service secret" in str(exc_info.value.detail)
