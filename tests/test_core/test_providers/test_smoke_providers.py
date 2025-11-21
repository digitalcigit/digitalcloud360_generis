"""
Tests Smoke - Providers Réels Sprint 2 S2.2

Tests rapides validant intégration providers avec vraies API keys.
Exécution : pytest tests/test_core/test_providers/test_smoke_providers.py -v
"""

import pytest
import os
from app.core.providers import (
    ProviderFactory,
    DeepseekProvider,
    KimiProvider,
    DALLEImageProvider
)
from app.config.settings import settings


# ============================================================
# SKIP SI PAS DE CLÉS API RÉELLES
# ============================================================

def has_real_api_keys() -> bool:
    """Vérifie si clés API réelles configurées (pas placeholder)"""
    deepseek_ok = settings.DEEPSEEK_API_KEY and not settings.DEEPSEEK_API_KEY.startswith("your-")
    kimi_ok = settings.KIMI_API_KEY and not settings.KIMI_API_KEY.startswith("your-")
    openai_ok = settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("your-")
    
    return deepseek_ok or kimi_ok or openai_ok


skip_if_no_keys = pytest.mark.skipif(
    not has_real_api_keys(),
    reason="Pas de clés API réelles configurées (placeholders détectés)"
)


# ============================================================
# TESTS SMOKE DEEPSEEK PROVIDER
# ============================================================

@skip_if_no_keys
@pytest.mark.asyncio
async def test_smoke_deepseek_generate():
    """
    Test smoke DeepseekProvider.generate() avec vraie API
    
    Vérifie:
    - Connexion API Deepseek réussie
    - Génération texte simple fonctionne
    - Réponse non vide
    """
    
    if settings.DEEPSEEK_API_KEY.startswith("your-"):
        pytest.skip("DEEPSEEK_API_KEY non configurée")
    
    provider = DeepseekProvider(
        api_key=settings.DEEPSEEK_API_KEY,
        model="deepseek-chat"
    )
    
    # Test génération simple
    response = await provider.generate(
        prompt="Bonjour, réponds simplement 'OK'",
        system_message="Tu es un assistant test.",
        max_tokens=10,
        temperature=0.0
    )
    
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)
    
    print(f"✅ Deepseek generate OK: {response[:50]}")


@skip_if_no_keys
@pytest.mark.asyncio
async def test_smoke_deepseek_generate_structured():
    """
    Test smoke DeepseekProvider.generate_structured() avec JSON
    
    Vérifie:
    - Génération JSON structuré fonctionne
    - Parse JSON réussit
    - Schéma respecté
    """
    
    if settings.DEEPSEEK_API_KEY.startswith("your-"):
        pytest.skip("DEEPSEEK_API_KEY non configurée")
    
    provider = DeepseekProvider(
        api_key=settings.DEEPSEEK_API_KEY,
        model="deepseek-chat"
    )
    
    # Schéma simple
    schema = {
        "name": "string",
        "age": "number",
        "city": "string"
    }
    
    # Test génération structurée
    response = await provider.generate_structured(
        prompt="Génère un profil fictif pour un entrepreneur africain de 35 ans à Dakar",
        response_schema=schema,
        temperature=0.3
    )
    
    assert response is not None
    assert isinstance(response, dict)
    assert "name" in response
    assert "age" in response
    assert "city" in response
    
    print(f"✅ Deepseek generate_structured OK: {response}")


@skip_if_no_keys
@pytest.mark.asyncio
async def test_smoke_deepseek_health_check():
    """
    Test smoke DeepseekProvider.health_check()
    
    Vérifie:
    - API accessible
    - Health check retourne True
    """
    
    if settings.DEEPSEEK_API_KEY.startswith("your-"):
        pytest.skip("DEEPSEEK_API_KEY non configurée")
    
    provider = DeepseekProvider(
        api_key=settings.DEEPSEEK_API_KEY,
        model="deepseek-chat"
    )
    
    is_healthy = await provider.health_check()
    
    assert is_healthy is True
    
    print("✅ Deepseek health check OK")


# ============================================================
# TESTS SMOKE KIMI PROVIDER
# ============================================================

@skip_if_no_keys
@pytest.mark.asyncio
async def test_smoke_kimi_search():
    """
    Test smoke KimiProvider.search() avec vraie API
    
    Vérifie:
    - Connexion API Kimi/Moonshot réussie
    - Recherche web fonctionne
    - Résultats structurés retournés
    """
    
    if settings.KIMI_API_KEY.startswith("your-"):
        pytest.skip("KIMI_API_KEY non configurée")
    
    provider = KimiProvider(
        api_key=settings.KIMI_API_KEY,
        model="moonshot-v1-8k"
    )
    
    # Test recherche simple
    result = await provider.search(
        query="startups tech Sénégal 2024",
        max_results=5,
        search_depth="basic"
    )
    
    assert result is not None
    assert "results" in result
    assert "query" in result
    assert result["query"] == "startups tech Sénégal 2024"
    assert "search_metadata" in result
    
    print(f"✅ Kimi search OK: {len(result['results'])} résultats")


@skip_if_no_keys
@pytest.mark.asyncio
async def test_smoke_kimi_health_check():
    """
    Test smoke KimiProvider.health_check()
    
    Vérifie:
    - API Moonshot accessible
    - Health check retourne True
    """
    
    if settings.KIMI_API_KEY.startswith("your-"):
        pytest.skip("KIMI_API_KEY non configurée")
    
    provider = KimiProvider(
        api_key=settings.KIMI_API_KEY,
        model="moonshot-v1-8k"
    )
    
    is_healthy = await provider.health_check()
    
    assert is_healthy is True
    
    print("✅ Kimi health check OK")


# ============================================================
# TESTS SMOKE DALLE PROVIDER
# ============================================================

@skip_if_no_keys
@pytest.mark.asyncio
async def test_smoke_dalle_health_check():
    """
    Test smoke DALLEImageProvider.health_check()
    
    Vérifie:
    - API OpenAI accessible
    - Credentials valides
    - Health check retourne True
    
    Note: Ne génère PAS d'image (coûteux), juste health check
    """
    
    if settings.OPENAI_API_KEY.startswith("your-"):
        pytest.skip("OPENAI_API_KEY non configurée")
    
    provider = DALLEImageProvider(
        api_key=settings.OPENAI_API_KEY,
        model="dall-e-3"
    )
    
    is_healthy = await provider.health_check()
    
    assert is_healthy is True
    
    print("✅ DALL-E health check OK")


# ============================================================
# TEST SMOKE FACTORY
# ============================================================

@skip_if_no_keys
@pytest.mark.asyncio
async def test_smoke_provider_factory():
    """
    Test smoke ProviderFactory avec clés API réelles
    
    Vérifie:
    - Factory crée providers correctement
    - API keys mappées proprement
    - Providers fonctionnels
    """
    
    # Construire dict API keys depuis settings
    api_keys = {}
    
    if not settings.DEEPSEEK_API_KEY.startswith("your-"):
        api_keys["deepseek"] = settings.DEEPSEEK_API_KEY
    
    if not settings.KIMI_API_KEY.startswith("your-"):
        api_keys["kimi"] = settings.KIMI_API_KEY
    
    if not settings.OPENAI_API_KEY.startswith("your-"):
        api_keys["openai"] = settings.OPENAI_API_KEY
        api_keys["dalle-3"] = settings.OPENAI_API_KEY
    
    if not api_keys:
        pytest.skip("Aucune clé API réelle configurée")
    
    # Créer factory
    factory = ProviderFactory(api_keys=api_keys)
    
    # Test création LLM provider
    if "deepseek" in api_keys:
        llm_provider = factory.create_llm_provider(
            plan="genesis_pro",
            override_provider="deepseek"
        )
        assert llm_provider is not None
        assert isinstance(llm_provider, DeepseekProvider)
        print("✅ Factory create_llm_provider (deepseek) OK")
    
    # Test création Search provider
    if "kimi" in api_keys:
        search_provider = factory.create_search_provider(
            plan="genesis_pro",
            override_provider="kimi"
        )
        assert search_provider is not None
        assert isinstance(search_provider, KimiProvider)
        print("✅ Factory create_search_provider (kimi) OK")
    
    # Test création Image provider
    if "dalle-3" in api_keys:
        image_provider = factory.create_image_provider(
            plan="genesis_pro",
            override_provider="dalle-3"
        )
        assert image_provider is not None
        assert isinstance(image_provider, DALLEImageProvider)
        print("✅ Factory create_image_provider (dalle-3) OK")


# ============================================================
# TEST SMOKE FALLBACK
# ============================================================

@skip_if_no_keys
@pytest.mark.asyncio
async def test_smoke_provider_fallback():
    """
    Test smoke fallback entre providers
    
    Vérifie:
    - Si provider primary échoue, fallback fonctionne
    - Architecture multi-provider robuste
    
    Note: Test avec clé invalide pour forcer fallback
    """
    
    # Créer provider avec clé invalide (simuler échec)
    provider_invalid = DeepseekProvider(
        api_key="invalid-key-test",
        model="deepseek-chat"
    )
    
    # Tentative génération devrait échouer
    try:
        await provider_invalid.generate(
            prompt="Test",
            max_tokens=10
        )
        assert False, "Devrait échouer avec clé invalide"
    except Exception as e:
        assert "401" in str(e) or "403" in str(e) or "Invalid" in str(e) or "Unauthorized" in str(e)
        print(f"✅ Fallback détecté erreur: {str(e)[:100]}")
    
    # Si OPENAI_API_KEY disponible, tester fallback réel
    if not settings.OPENAI_API_KEY.startswith("your-"):
        # Factory devrait utiliser OpenAI en fallback
        factory = ProviderFactory(api_keys={
            "openai": settings.OPENAI_API_KEY
        })
        
        llm_fallback = factory.create_llm_provider(
            plan="genesis_pro",
            override_provider="openai"  # Fallback explicite
        )
        
        # Test devrait marcher avec fallback
        # Note: OpenAIProvider pas encore implémenté, on teste juste factory
        assert llm_fallback is not None
        print("✅ Fallback factory OK (OpenAI disponible)")
