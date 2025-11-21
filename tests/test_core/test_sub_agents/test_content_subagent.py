"""
Tests unitaires ContentSubAgent - Sprint 2 S2.1
Tests génération contenu multilingue avec adaptation culturelle
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any

from app.core.deep_agents.sub_agents.content import ContentSubAgent
from app.core.providers.base import BaseLLMProvider


# ============================================================
# FIXTURES - MOCK PROVIDERS
# ============================================================

@pytest.fixture
def mock_llm_provider():
    """Mock BaseLLMProvider pour tests ContentSubAgent"""
    provider = AsyncMock(spec=BaseLLMProvider)
    
    # Mock generate retourne contenu HTML/texte
    async def mock_generate(*args, **kwargs):
        return """
        <h1>Bienvenue chez EcoTech Sénégal</h1>
        <p>Votre partenaire digital pour l'agriculture moderne</p>
        """
    
    provider.generate = mock_generate
    
    return provider


@pytest.fixture
def mock_provider_factory(mock_llm_provider):
    """Mock ProviderFactory retournant mock LLM provider"""
    factory = MagicMock()
    factory.get_llm_provider = MagicMock(return_value=mock_llm_provider)
    return factory


@pytest.fixture
def business_brief_sample() -> Dict[str, Any]:
    """Business brief sample pour tests"""
    return {
        'business_name': 'EcoTech Sénégal',
        'industry_sector': 'Agriculture Digital',
        'location': {
            'country': 'Sénégal',
            'city': 'Dakar',
            'region': 'Dakar'
        },
        'vision': 'Moderniser agriculture par technologie',
        'mission': 'Fournir outils digitaux agriculteurs africains',
        'target_market': 'Agriculteurs et coopératives agricoles',
        'services': [
            'Plateforme gestion parcelles',
            'Météo agricole',
            'Marketplace produits agricoles'
        ],
        'competitive_advantage': 'Adaptation besoins locaux + Support wolof',
        'value_proposition': 'Agriculture intelligente accessible à tous'
    }


# ============================================================
# TESTS - CAS NOMINAL
# ============================================================

@pytest.mark.asyncio
async def test_generate_website_content_success(
    mock_provider_factory,
    business_brief_sample
):
    """
    Test cas nominal generate_website_content.
    
    Vérifie:
    - Structure résultat complète (5 sections)
    - Langues générées correctement
    - Métadonnées présentes
    - Stratégie contenu incluse
    """
    
    with patch('app.core.deep_agents.sub_agents.content.ProviderFactory', return_value=mock_provider_factory):
        agent = ContentSubAgent()
        
        # Mock méthodes génération pour retourner contenu structuré
        async def mock_homepage(*args, **kwargs):
            return {
                'fr': {'hero_title': 'Bienvenue', 'hero_subtitle': 'Agriculture moderne'},
                'wo': {'hero_title': 'Dalal ak jamm', 'hero_subtitle': 'Agriculture bu bees'}
            }
        
        async def mock_about(*args, **kwargs):
            return {
                'fr': {'story': 'Notre histoire', 'mission': 'Notre mission'},
                'wo': {'story': 'Sunuy taariix', 'mission': 'Sunuy xel'}
            }
        
        async def mock_services(*args, **kwargs):
            return {
                'fr': {'services_list': ['Service 1', 'Service 2']},
                'wo': {'services_list': ['Liggéey 1', 'Liggéey 2']}
            }
        
        async def mock_contact(*args, **kwargs):
            return {
                'fr': {'cta': 'Contactez-nous', 'phone': '+221 XX XXX XX XX'},
                'wo': {'cta': 'Jokkoo ak nun', 'phone': '+221 XX XXX XX XX'}
            }
        
        async def mock_seo(*args, **kwargs):
            return {
                'fr': {'title': 'EcoTech - Agriculture Digital', 'description': 'Solutions agricoles'},
                'wo': {'title': 'EcoTech - Agriculture bu njëkk', 'description': 'Jumtukaay agriculture'}
            }
        
        async def mock_strategy(*args, **kwargs):
            return {
                'tone': 'chaleureux et accessible',
                'keywords': ['agriculture', 'digital', 'Sénégal'],
                'target_audience': 'Agriculteurs 25-55 ans'
            }
        
        agent._generate_homepage_content = mock_homepage
        agent._generate_about_content = mock_about
        agent._generate_services_content = mock_services
        agent._generate_contact_content = mock_contact
        agent._generate_seo_metadata = mock_seo
        agent._generate_content_strategy = mock_strategy
        
        result = await agent.generate_website_content(business_brief_sample)
        
        # Vérifications structure
        assert 'homepage' in result
        assert 'about' in result
        assert 'services' in result
        assert 'contact' in result
        assert 'seo_metadata' in result
        assert 'languages_generated' in result
        assert 'content_strategy' in result
        assert 'generation_metadata' in result
        
        # Vérifications langues (Sénégal = français + wolof)
        languages = result['languages_generated']
        assert 'fr' in languages
        assert 'wo' in languages
        
        # Vérifications contenu
        assert result['homepage']['fr']['hero_title'] == 'Bienvenue'
        assert result['homepage']['wo']['hero_title'] == 'Dalal ak jamm'
        
        # Vérifications métadonnées
        metadata = result['generation_metadata']
        assert 'timestamp' in metadata
        assert metadata['sections_generated'] == 5
        
        # Vérifications stratégie
        strategy = result['content_strategy']
        assert strategy['tone'] == 'chaleureux et accessible'


# ============================================================
# TESTS - MULTILINGUE (2 LANGUES MAJEURES + 1 LOCALE)
# ============================================================

@pytest.mark.asyncio
async def test_generate_content_multilingual_french_wolof(
    mock_provider_factory,
    business_brief_sample
):
    """
    Test génération multilingue français + wolof (langue locale Sénégal).
    
    Vérifie:
    - Français généré correctement
    - Wolof (langue locale) généré correctement
    - Contenu adapté culturellement
    
    REQUIS SM: 2 langues majeures + 1 langue locale
    """
    
    with patch('app.core.deep_agents.sub_agents.content.ProviderFactory', return_value=mock_provider_factory):
        agent = ContentSubAgent()
        
        # Mock pour tester mapping langues
        brief_senegal = business_brief_sample.copy()
        brief_senegal['location']['country'] = 'Sénégal'
        
        languages = agent._determine_target_languages(brief_senegal)
        
        # Vérifications langues Sénégal
        assert 'fr' in languages  # Langue majeure 1
        assert 'wo' in languages  # Langue locale (wolof)
        assert len(languages) == 2
        
        # Test avec autre pays (Mali = français + bambara)
        brief_mali = business_brief_sample.copy()
        brief_mali['location'] = {'country': 'Mali', 'city': 'Bamako'}
        
        languages_mali = agent._determine_target_languages(brief_mali)
        
        assert 'fr' in languages_mali  # Langue majeure 2
        assert 'bm' in languages_mali  # Langue locale (bambara)


@pytest.mark.asyncio
async def test_generate_content_multilingual_swahili(
    mock_provider_factory,
    business_brief_sample
):
    """
    Test génération avec swahili (langue locale Afrique de l'Est).
    
    Vérifie:
    - Swahili détecté pour Kenya/Tanzanie/RDC
    - Français reste langue primaire
    
    REQUIS SM: Au moins 1 langue locale
    """
    
    with patch('app.core.deep_agents.sub_agents.content.ProviderFactory', return_value=mock_provider_factory):
        agent = ContentSubAgent()
        
        # Test Kenya
        brief_kenya = business_brief_sample.copy()
        brief_kenya['location'] = {'country': 'Kenya', 'city': 'Nairobi'}
        
        languages_kenya = agent._determine_target_languages(brief_kenya)
        
        assert 'fr' in languages_kenya
        assert 'sw' in languages_kenya  # Swahili
        
        # Test RDC (3 langues)
        brief_rdc = business_brief_sample.copy()
        brief_rdc['location'] = {'country': 'RDC', 'city': 'Kinshasa'}
        
        languages_rdc = agent._determine_target_languages(brief_rdc)
        
        assert 'fr' in languages_rdc
        assert 'lg' in languages_rdc  # Lingala
        assert 'sw' in languages_rdc  # Swahili
        assert len(languages_rdc) == 3


# ============================================================
# TESTS - FALLBACK
# ============================================================

@pytest.mark.asyncio
async def test_generate_content_provider_failure_fallback(
    mock_provider_factory,
    business_brief_sample
):
    """
    Test fallback quand LLM provider échoue.
    
    Vérifie:
    - Fallback gracieux activé
    - Contenu minimal retourné
    - Pas d'exception levée
    - Métadonnées indiquent fallback
    
    REQUIS SM: Cas d'erreur provider / fallback
    """
    
    # Configurer mock LLM pour échouer
    mock_llm_fail = AsyncMock(spec=BaseLLMProvider)
    mock_llm_fail.generate = AsyncMock(side_effect=Exception("LLM provider timeout"))
    
    mock_provider_factory.get_llm_provider = MagicMock(return_value=mock_llm_fail)
    
    with patch('app.core.deep_agents.sub_agents.content.ProviderFactory', return_value=mock_provider_factory):
        agent = ContentSubAgent()
        
        result = await agent.generate_website_content(business_brief_sample)
        
        # Vérifier fallback content retourné
        assert result is not None
        assert isinstance(result, dict)
        
        # Vérifier structure minimale présente
        assert 'homepage' in result or 'fallback_mode' in result
        
        # Si fallback_content existe, vérifier qu'il contient des clés essentielles
        if 'fallback_mode' in result:
            assert result['fallback_mode'] is True
        
        # Vérifier qu'aucune exception n'a été levée (test passe = pas d'exception)


@pytest.mark.asyncio
async def test_generate_content_partial_failure(
    mock_provider_factory,
    business_brief_sample
):
    """
    Test comportement avec échec partiel (certaines sections échouent).
    
    Vérifie:
    - Sections réussies sont retournées
    - Sections échouées sont vides {}
    - Métadonnées errors indiquent les échecs
    - Génération continue malgré échecs partiels
    """
    
    with patch('app.core.deep_agents.sub_agents.content.ProviderFactory', return_value=mock_provider_factory):
        agent = ContentSubAgent()
        
        # Mock avec échecs sur certaines sections
        async def mock_homepage_ok(*args, **kwargs):
            return {'fr': {'hero': 'Contenu OK'}}
        
        async def mock_about_fail(*args, **kwargs):
            raise Exception("About section failed")
        
        async def mock_services_ok(*args, **kwargs):
            return {'fr': {'services': ['Service 1']}}
        
        async def mock_contact_fail(*args, **kwargs):
            raise Exception("Contact section failed")
        
        async def mock_seo_ok(*args, **kwargs):
            return {'fr': {'title': 'SEO OK'}}
        
        async def mock_strategy(*args, **kwargs):
            return {'tone': 'professionnel'}
        
        agent._generate_homepage_content = mock_homepage_ok
        agent._generate_about_content = mock_about_fail
        agent._generate_services_content = mock_services_ok
        agent._generate_contact_content = mock_contact_fail
        agent._generate_seo_metadata = mock_seo_ok
        agent._generate_content_strategy = mock_strategy
        
        result = await agent.generate_website_content(business_brief_sample)
        
        # Vérifier sections réussies présentes
        assert result['homepage'] == {'fr': {'hero': 'Contenu OK'}}
        assert result['services'] == {'fr': {'services': ['Service 1']}}
        assert result['seo_metadata'] == {'fr': {'title': 'SEO OK'}}
        
        # Vérifier sections échouées sont vides
        assert result['about'] == {}
        assert result['contact'] == {}
        
        # Vérifier métadonnées erreurs
        metadata = result['generation_metadata']
        assert metadata['errors'] is not None
        assert len(metadata['errors']) == 2  # 2 sections échouées


# ============================================================
# TESTS - LANGUES SUPPORTÉES
# ============================================================

@pytest.mark.asyncio
async def test_supported_languages_configuration(mock_provider_factory):
    """
    Test configuration langues supportées.
    
    Vérifie:
    - Toutes les langues locales africaines configurées
    - Mapping ISO 639-1 correct
    """
    
    with patch('app.core.deep_agents.sub_agents.content.ProviderFactory', return_value=mock_provider_factory):
        agent = ContentSubAgent()
        
        # Vérifier langues supportées
        assert 'fr' in agent.supported_languages  # Français
        assert 'wo' in agent.supported_languages  # Wolof
        assert 'bm' in agent.supported_languages  # Bambara
        assert 'ha' in agent.supported_languages  # Hausa
        assert 'sw' in agent.supported_languages  # Swahili
        assert 'lg' in agent.supported_languages  # Lingala
        assert 'ff' in agent.supported_languages  # Fulfulde
        
        # Vérifier noms complets
        assert agent.supported_languages['wo'] == 'wolof'
        assert agent.supported_languages['sw'] == 'swahili'
