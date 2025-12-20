import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.agents.seo import SeoAgent


@pytest.fixture
def mock_tavily_client():
    """Mock Tavily search client for testing"""
    with patch('app.core.agents.seo.TavilyClient') as mock:
        client_instance = AsyncMock()
        client_instance.search_market = AsyncMock(return_value={
            "results": [
                {"title": "Competitor 1", "url": "https://example.com"},
                {"title": "Competitor 2", "url": "https://example2.com"}
            ],
            "query": "SEO technology France"
        })
        mock.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_deepseek_provider():
    """Mock Deepseek LLM provider for testing"""
    with patch('app.core.agents.seo.DeepseekProvider') as mock:
        provider_instance = AsyncMock()
        provider_instance.generate_structured = AsyncMock(return_value={
            "primary_keywords": ["software", "technology", "innovation"],
            "secondary_keywords": ["development", "solutions", "digital", "services", "consulting"],
            "meta_title": "Test Company - Software & Technology Solutions",
            "meta_description": "Leading provider of innovative software solutions for modern businesses. Expert technology consulting and digital transformation services.",
            "heading_structure": {
                "h1": "Transform Your Business with Innovative Technology",
                "h2_sections": [
                    "Our Services",
                    "Why Choose Us",
                    "Case Studies",
                    "Get Started"
                ]
            },
            "local_seo": {
                "optimized_for": "Paris, France",
                "local_keywords": ["software Paris", "tech France"]
            }
        })
        mock.return_value = provider_instance
        yield provider_instance


@pytest.mark.asyncio
async def test_seo_agent_generate_success(mock_tavily_client, mock_deepseek_provider):
    """Test successful SEO generation via Deepseek LLM"""
    agent = SeoAgent()
    
    result = await agent.run(
        business_name="Test Company",
        business_description="We provide innovative software solutions",
        industry_sector="technology",
        target_location={"country": "France", "city": "Paris"}
    )
    
    assert result is not None
    assert "primary_keywords" in result
    assert len(result["primary_keywords"]) >= 3
    assert "meta_title" in result
    assert "meta_description" in result
    assert result["metadata"]["agent"] == "SeoAgent"
    assert result["metadata"]["business_name"] == "Test Company"
    
    # Verify Tavily search was called
    mock_tavily_client.search_market.assert_called_once()
    
    # Verify Deepseek LLM was called
    mock_deepseek_provider.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_seo_agent_with_location(mock_tavily_client, mock_deepseek_provider):
    """Test SEO generation with location data"""
    agent = SeoAgent()
    
    result = await agent.run(
        business_name="Local Business",
        business_description="Local services provider",
        industry_sector="consulting",
        target_location={"country": "Senegal", "city": "Dakar"}
    )
    
    # Verify location was used in search query
    call_args = mock_tavily_client.search_market.call_args
    search_query = call_args.kwargs["query"]
    assert "consulting" in search_query.lower()
    assert "Dakar" in search_query or "Senegal" in search_query
    
    # Check local SEO in result (mock returns Paris, but we verify structure)
    assert "local_seo" in result
    assert "optimized_for" in result["local_seo"]
    assert "local_keywords" in result["local_seo"]


@pytest.mark.asyncio
async def test_seo_agent_without_location(mock_tavily_client, mock_deepseek_provider):
    """Test SEO generation without location data"""
    agent = SeoAgent()
    
    result = await agent.run(
        business_name="Global Business",
        business_description="Global services provider",
        industry_sector="e-commerce"
    )
    
    assert result is not None
    assert "primary_keywords" in result
    
    # Verify search was still performed
    mock_tavily_client.search_market.assert_called_once()


@pytest.mark.asyncio
async def test_seo_agent_with_unique_value_proposition(mock_tavily_client, mock_deepseek_provider):
    """Test SEO generation with unique value proposition"""
    agent = SeoAgent()
    
    uvp = "First AI-powered platform for African businesses"
    
    result = await agent.run(
        business_name="InnovCorp",
        business_description="Technology solutions",
        industry_sector="software",
        unique_value_proposition=uvp
    )
    
    # Verify UVP was passed to LLM prompt
    call_args = mock_deepseek_provider.generate_structured.call_args
    prompt = call_args.kwargs["prompt"]
    assert uvp in prompt


@pytest.mark.asyncio
async def test_seo_agent_fallback_on_llm_error(mock_tavily_client, mock_deepseek_provider):
    """Test fallback SEO when LLM fails"""
    mock_deepseek_provider.generate_structured.side_effect = Exception("LLM API error")
    
    agent = SeoAgent()
    result = await agent.run(
        business_name="Fallback Business",
        business_description="We provide quality services",
        industry_sector="consulting"
    )
    
    assert result is not None
    assert result["metadata"]["fallback"] is True
    assert "error" in result["metadata"]
    
    # Fallback should still provide basic SEO
    assert "primary_keywords" in result
    assert "meta_title" in result
    assert "Fallback Business" in result["meta_title"]


@pytest.mark.asyncio
async def test_seo_agent_meta_title_length(mock_tavily_client, mock_deepseek_provider):
    """Test that meta title is within SEO best practices"""
    agent = SeoAgent()
    
    result = await agent.run(
        business_name="Test",
        business_description="Test description",
        industry_sector="services"
    )
    
    meta_title = result["meta_title"]
    # SEO best practice: 50-60 characters
    assert len(meta_title) >= 30
    assert len(meta_title) <= 70


@pytest.mark.asyncio
async def test_seo_agent_meta_description_length(mock_tavily_client, mock_deepseek_provider):
    """Test that meta description is within SEO best practices"""
    agent = SeoAgent()
    
    result = await agent.run(
        business_name="Test",
        business_description="Test description",
        industry_sector="services"
    )
    
    meta_description = result["meta_description"]
    # SEO best practice: 150-160 characters
    assert len(meta_description) >= 100
    assert len(meta_description) <= 170


@pytest.mark.asyncio
async def test_seo_agent_heading_structure(mock_tavily_client, mock_deepseek_provider):
    """Test that heading structure is properly generated"""
    agent = SeoAgent()
    
    result = await agent.run(
        business_name="Test",
        business_description="Test description",
        industry_sector="services"
    )
    
    assert "heading_structure" in result
    assert "h1" in result["heading_structure"]
    assert "h2_sections" in result["heading_structure"]
    assert isinstance(result["heading_structure"]["h2_sections"], list)
    assert len(result["heading_structure"]["h2_sections"]) >= 3


@pytest.mark.asyncio
async def test_seo_agent_keywords_count(mock_tavily_client, mock_deepseek_provider):
    """Test that proper number of keywords are generated"""
    agent = SeoAgent()
    
    result = await agent.run(
        business_name="Test",
        business_description="Test description",
        industry_sector="services"
    )
    
    # Primary keywords: 3-5
    assert len(result["primary_keywords"]) >= 3
    assert len(result["primary_keywords"]) <= 5
    
    # Secondary keywords: 5-8
    assert len(result["secondary_keywords"]) >= 5
    assert len(result["secondary_keywords"]) <= 8
