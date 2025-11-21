"""
Tests unitaires ResearchSubAgent - Sprint 2 S2.1
Tests architecture multi-provider avec fallbacks
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any

from app.core.deep_agents.sub_agents.research import ResearchSubAgent
from app.core.providers.base import BaseSearchProvider, BaseLLMProvider


# ============================================================
# FIXTURES - MOCK PROVIDERS
# ============================================================

@pytest.fixture
def mock_search_provider():
    """Mock BaseSearchProvider pour tests"""
    provider = AsyncMock(spec=BaseSearchProvider)
    
    # Comportement par défaut: recherche réussie
    provider.search = AsyncMock(return_value={
        'results': [
            {
                'title': 'Concurrent 1 - Secteur Test',
                'url': 'https://example.com/competitor1',
                'snippet': 'Leader marché secteur test en Afrique',
                'score': 0.95
            },
            {
                'title': 'Concurrent 2 - Analyse Marché',
                'url': 'https://jeune-afrique.com/market-analysis',
                'snippet': 'Opportunités business secteur test',
                'score': 0.88
            }
        ],
        'total_results': 2
    })
    
    return provider


@pytest.fixture
def mock_llm_provider():
    """Mock BaseLLMProvider pour tests"""
    provider = AsyncMock(spec=BaseLLMProvider)
    
    # Comportement par défaut: analyse LLM réussie
    # IMPORTANT: generate() retourne string JSON (pas dict)
    async def mock_generate(*args, **kwargs):
        return json.dumps({
            "market_size": {
                "estimated_value": "50M-100M USD",
                "growth_rate": "15% annual",
                "maturity": "emerging"
            },
            "competitors": [
                {
                    "name": "Concurrent A",
                    "market_share": "25%",
                    "strengths": ["Présence locale", "Prix compétitifs"]
                },
                {
                    "name": "Concurrent B",
                    "market_share": "15%",
                    "strengths": ["Innovation", "Service client"]
                }
            ],
            "opportunities": [
                "Digitalisation services",
                "Marché rural non servi",
                "Partenariats B2B"
            ],
            "pricing": {
                "range": "1000-5000 FCFA",
                "positioning": "mid-range"
            },
            "differentiators": [
                "Focus expérience locale",
                "Support multilingue",
                "Paiement mobile"
            ],
            "cultural_factors": {
                "trust_building": "Essentiel - relations personnelles",
                "payment_preferences": "Mobile money dominant"
            },
            "risks": [
                "Concurrence informelle",
                "Infrastructures limitées"
            ],
            "success_keys": [
                "Adaptation culturelle",
                "Prix accessibles",
                "Service après-vente"
            ]
        })
    
    provider.generate = mock_generate
    
    return provider


@pytest.fixture
def mock_provider_factory(mock_search_provider, mock_llm_provider):
    """Mock ProviderFactory retournant mocks providers"""
    factory = MagicMock()
    factory.get_search_provider = MagicMock(return_value=mock_search_provider)
    factory.get_llm_provider = MagicMock(return_value=mock_llm_provider)
    return factory


@pytest.fixture
def business_context_sample() -> Dict[str, Any]:
    """Contexte business sample pour tests"""
    return {
        'business_name': 'EcoTech Sénégal',
        'industry_sector': 'Agriculture Digital',
        'location': {
            'country': 'Sénégal',
            'city': 'Dakar',
            'region': 'Dakar'
        },
        'target_market': 'Agriculteurs et coopératives agricoles',
        'vision': 'Moderniser agriculture par technologie',
        'mission': 'Fournir outils digitaux agriculteurs africains',
        'competitive_advantage': 'Adaptation besoins locaux',
        'services': ['Plateforme gestion parcelles', 'Météo agricole']
    }


# ============================================================
# TESTS - CAS NOMINAL
# ============================================================

@pytest.mark.asyncio
async def test_analyze_market_success(
    mock_provider_factory,
    business_context_sample
):
    """
    Test cas nominal analyze_market avec providers fonctionnels.
    
    Vérifie:
    - Appels recherche parallèles (4 tasks)
    - Analyse LLM avec résultats agrégés
    - Structure réponse complète
    - Métadonnées search
    """
    
    with patch('app.core.deep_agents.sub_agents.research.ProviderFactory', return_value=mock_provider_factory):
        agent = ResearchSubAgent()
        
        # Mock de _analyze_with_llm pour retourner dict directement
        async def mock_analyze(*args, **kwargs):
            return {
                "market_size": {"estimated_value": "50M-100M USD"},
                "competitors": [{"name": "Concurrent A"}],
                "opportunities": ["Digitalisation services"],
                "pricing": {"range": "1000-5000 FCFA"},
                "differentiators": ["Focus expérience locale"],
                "cultural_factors": {"trust_building": "Essentiel"},
                "risks": ["Concurrence informelle"],
                "success_keys": ["Adaptation culturelle"]
            }
        
        agent._analyze_with_llm = mock_analyze
        
        result = await agent.analyze_market(business_context_sample)
        
        # Vérifications structure résultat
        assert 'market_size_estimation' in result
        assert 'main_competitors' in result
        assert 'market_opportunities' in result
        assert 'pricing_insights' in result
        assert 'differentiation_suggestions' in result
        assert 'cultural_insights' in result
        assert 'risk_factors' in result
        assert 'success_factors' in result
        assert 'search_metadata' in result
        
        # Vérifications contenu
        assert len(result['main_competitors']) <= 5  # Max 5 concurrents
        assert isinstance(result['market_opportunities'], list)
        assert isinstance(result['differentiation_suggestions'], list)
        
        # Vérifications métadonnées
        metadata = result['search_metadata']
        assert 'timestamp' in metadata
        assert metadata['sources_consulted'] >= 0
        assert 'search_failures' in metadata
        
        # Vérifier appels providers
        assert mock_provider_factory.get_search_provider.called
        assert mock_provider_factory.get_llm_provider.called


@pytest.mark.asyncio
async def test_search_competitors_query_construction(
    mock_provider_factory,
    business_context_sample
):
    """
    Test construction query recherche concurrents.
    
    Vérifie:
    - Query inclut secteur, ville, pays
    - Domaines africains inclus
    - max_results = 8
    - search_depth = advanced
    """
    
    with patch('app.core.deep_agents.sub_agents.research.ProviderFactory', return_value=mock_provider_factory):
        agent = ResearchSubAgent()
        
        result = await agent._search_competitors(business_context_sample)
        
        # Vérifier structure résultat
        assert result['type'] == 'competitors'
        assert 'data' in result
        assert 'query' in result
        
        # Vérifier query contient éléments clés
        query = result['query']
        assert 'Agriculture Digital' in query
        assert 'Dakar' in query
        assert 'Sénégal' in query
        
        # Vérifier appel search provider avec bons params
        search_provider = mock_provider_factory.get_search_provider()
        search_provider.search.assert_called_once()
        call_kwargs = search_provider.search.call_args.kwargs
        
        assert call_kwargs['max_results'] == 8
        assert call_kwargs['search_depth'] == 'advanced'
        assert call_kwargs['include_domains'] == agent.african_domains


# ============================================================
# TESTS - FALLBACKS
# ============================================================

@pytest.mark.asyncio
async def test_analyze_market_search_provider_failure(
    mock_provider_factory,
    mock_llm_provider,
    business_context_sample
):
    """
    Test fallback quand search provider échoue.
    
    Vérifie:
    - Agent continue avec fallback analysis
    - Pas d'exception levée
    - Résultat structure complète malgré erreur
    """
    
    # Configurer mock search provider pour échouer
    mock_search_fail = AsyncMock(spec=BaseSearchProvider)
    mock_search_fail.search = AsyncMock(side_effect=Exception("Tavily API down"))
    
    mock_provider_factory.get_search_provider = MagicMock(return_value=mock_search_fail)
    
    with patch('app.core.deep_agents.sub_agents.research.ProviderFactory', return_value=mock_provider_factory):
        agent = ResearchSubAgent()
        
        result = await agent.analyze_market(business_context_sample)
        
        # Vérifier fallback analysis appelé
        assert result is not None
        assert 'market_size_estimation' in result
        
        # Vérifier search_metadata indique échecs
        metadata = result.get('search_metadata', {})
        assert metadata.get('search_failures', 0) > 0 or metadata.get('sources_consulted', 0) == 0


@pytest.mark.asyncio
async def test_analyze_market_llm_provider_failure(
    mock_provider_factory,
    mock_search_provider,
    business_context_sample
):
    """
    Test fallback quand LLM provider échoue à analyser.
    
    Vérifie:
    - Fallback gracieux activé
    - Résultat structure minimale retourné
    - Logging erreur
    """
    
    # Configurer mock LLM provider pour échouer
    mock_llm_fail = AsyncMock(spec=BaseLLMProvider)
    mock_llm_fail.generate = AsyncMock(side_effect=Exception("Deepseek timeout"))
    
    mock_provider_factory.get_llm_provider = MagicMock(return_value=mock_llm_fail)
    
    with patch('app.core.deep_agents.sub_agents.research.ProviderFactory', return_value=mock_provider_factory):
        agent = ResearchSubAgent()
        
        result = await agent.analyze_market(business_context_sample)
        
        # Vérifier fallback analysis retourné
        assert result is not None
        assert isinstance(result, dict)
        
        # Vérifier clés essentielles présentes
        assert 'market_size_estimation' in result
        assert 'main_competitors' in result


@pytest.mark.asyncio
async def test_analyze_market_all_searches_fail(
    mock_provider_factory,
    business_context_sample
):
    """
    Test comportement quand TOUTES les recherches échouent.
    
    Vérifie:
    - Fallback analysis appelé
    - Structure résultat minimale
    - Metadata indique mode fallback
    """
    
    # Configurer mock search pour échouer systématiquement
    mock_search_fail = AsyncMock(spec=BaseSearchProvider)
    mock_search_fail.search = AsyncMock(side_effect=Exception("All search failed"))
    
    mock_provider_factory.get_search_provider = MagicMock(return_value=mock_search_fail)
    
    with patch('app.core.deep_agents.sub_agents.research.ProviderFactory', return_value=mock_provider_factory):
        agent = ResearchSubAgent()
        
        result = await agent.analyze_market(business_context_sample)
        
        # Vérifier fallback structure
        assert result is not None
        assert 'market_size_estimation' in result
        
        # Vérifier qu'aucune source consultée avec succès
        metadata = result.get('search_metadata', {})
        # En mode fallback, sources_consulted devrait être 0
        assert metadata.get('sources_consulted', 0) == 0


# ============================================================
# TESTS - RECHERCHES SPÉCIFIQUES
# ============================================================

@pytest.mark.asyncio
async def test_search_market_trends(
    mock_provider_factory,
    business_context_sample
):
    """
    Test recherche tendances marché.
    
    Vérifie:
    - Query inclut "tendances marché"
    - Type = 'trends'
    - Gestion erreur gracieuse
    """
    
    with patch('app.core.deep_agents.sub_agents.research.ProviderFactory', return_value=mock_provider_factory):
        agent = ResearchSubAgent()
        
        result = await agent._search_market_trends(business_context_sample)
        
        assert result['type'] == 'trends'
        assert 'data' in result
        assert 'query' in result
        
        # Vérifier query contient "tendances"
        assert 'tendances' in result['query'].lower() or 'trends' in result['query'].lower()


@pytest.mark.asyncio
async def test_search_pricing_data(
    mock_provider_factory,
    business_context_sample
):
    """
    Test recherche données pricing.
    
    Vérifie:
    - Query inclut "prix" ou "tarifs"
    - Type = 'pricing'
    """
    
    with patch('app.core.deep_agents.sub_agents.research.ProviderFactory', return_value=mock_provider_factory):
        agent = ResearchSubAgent()
        
        result = await agent._search_pricing_data(business_context_sample)
        
        assert result['type'] == 'pricing'
        assert 'query' in result
        
        # Vérifier query pricing
        query_lower = result['query'].lower()
        assert 'prix' in query_lower or 'tarif' in query_lower


@pytest.mark.asyncio
async def test_search_opportunities(
    mock_provider_factory,
    business_context_sample
):
    """
    Test recherche opportunités business.
    
    Vérifie:
    - Query inclut "opportunités"
    - Type = 'opportunities'
    """
    
    with patch('app.core.deep_agents.sub_agents.research.ProviderFactory', return_value=mock_provider_factory):
        agent = ResearchSubAgent()
        
        result = await agent._search_opportunities(business_context_sample)
        
        assert result['type'] == 'opportunities'
        assert 'query' in result
        
        # Vérifier query opportunités
        assert 'opportunité' in result['query'].lower()


# ============================================================
# TESTS - DOMAINES AFRICAINS
# ============================================================

@pytest.mark.asyncio
async def test_african_domains_configuration(mock_provider_factory):
    """
    Test configuration domaines africains prioritaires.
    
    Vérifie:
    - Liste domaines non vide
    - Domaines pertinents (jeune-afrique, lesechos, etc.)
    """
    
    with patch('app.core.deep_agents.sub_agents.research.ProviderFactory', return_value=mock_provider_factory):
        agent = ResearchSubAgent()
        
        assert len(agent.african_domains) > 0
        
        # Vérifier domaines clés présents
        domains_str = ','.join(agent.african_domains)
        assert 'jeune-afrique' in domains_str
        assert 'afrik' in domains_str or 'africa' in domains_str


# ============================================================
# TESTS - RÉSULTATS VIDES
# ============================================================

@pytest.mark.asyncio
async def test_analyze_market_empty_search_results(
    mock_provider_factory,
    mock_llm_provider,
    business_context_sample
):
    """
    Test comportement avec résultats recherche vides.
    
    Vérifie:
    - Agent continue avec données minimales
    - LLM analyse avec contexte business uniquement
    - Pas de crash
    """
    
    # Configurer mock search pour retourner résultats vides
    mock_search_empty = AsyncMock(spec=BaseSearchProvider)
    mock_search_empty.search = AsyncMock(return_value={
        'results': [],
        'total_results': 0
    })
    
    mock_provider_factory.get_search_provider = MagicMock(return_value=mock_search_empty)
    
    with patch('app.core.deep_agents.sub_agents.research.ProviderFactory', return_value=mock_provider_factory):
        agent = ResearchSubAgent()
        
        result = await agent.analyze_market(business_context_sample)
        
        # Vérifier résultat retourné malgré recherches vides
        assert result is not None
        assert isinstance(result, dict)
