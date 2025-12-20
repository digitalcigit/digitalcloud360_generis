import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.agents.logo import LogoAgent


@pytest.fixture
def mock_dalle_provider():
    """Mock DALL-E provider for testing"""
    with patch('app.core.agents.logo.DALLEImageProvider') as mock:
        provider_instance = AsyncMock()
        provider_instance.generate_logo = AsyncMock(return_value={
            "image_url": "https://example.com/logo.png",
            "image_data": None,
            "prompt_used": "A professional logo for Test Company",
            "metadata": {
                "provider": "dalle",
                "model": "dall-e-3",
                "size": "1024x1024",
                "quality": "hd"
            }
        })
        mock.return_value = provider_instance
        yield provider_instance


@pytest.fixture
def mock_redis_fs():
    """Mock Redis filesystem for testing"""
    with patch('app.core.agents.logo.RedisVirtualFileSystem') as mock:
        redis_instance = AsyncMock()
        redis_instance.read_file = AsyncMock(return_value=None)
        redis_instance.write_file = AsyncMock()
        mock.return_value = redis_instance
        yield redis_instance


@pytest.mark.asyncio
async def test_logo_agent_generate_success(mock_dalle_provider, mock_redis_fs):
    """Test successful logo generation via DALL-E 3"""
    agent = LogoAgent()
    
    result = await agent.run(
        company_name="Test Company",
        industry="technology",
        style="modern"
    )
    
    assert result is not None
    assert "logo_url" in result
    assert result["logo_url"] == "https://example.com/logo.png"
    assert result["cached"] is False
    assert result["metadata"]["agent"] == "LogoAgent"
    assert result["metadata"]["company_name"] == "Test Company"
    
    # Verify DALL-E was called with correct params
    mock_dalle_provider.generate_logo.assert_called_once()
    call_kwargs = mock_dalle_provider.generate_logo.call_args.kwargs
    assert call_kwargs["business_name"] == "Test Company"
    assert call_kwargs["industry"] == "technology"


@pytest.mark.asyncio
async def test_logo_agent_style_adaptation(mock_dalle_provider, mock_redis_fs):
    """Test industry-based style adaptation"""
    agent = LogoAgent()
    
    # Test restaurant industry should get 'elegant' style
    await agent.run(
        company_name="Gourmet Cafe",
        industry="restaurant",
        style="modern"  # Will be adapted to 'elegant'
    )
    
    call_kwargs = mock_dalle_provider.generate_logo.call_args.kwargs
    assert call_kwargs["style"] == "elegant"
    
    # Test tech industry should get 'tech' style
    await agent.run(
        company_name="TechCorp",
        industry="software",
        style="modern"
    )
    
    call_kwargs = mock_dalle_provider.generate_logo.call_args.kwargs
    assert call_kwargs["style"] == "tech"


@pytest.mark.asyncio
async def test_logo_agent_cache_hit(mock_dalle_provider, mock_redis_fs):
    """Test logo retrieval from cache"""
    import json
    
    cached_logo = {
        "logo_url": "https://cached.com/logo.png",
        "logo_data": None,
        "metadata": {"cached": True}
    }
    
    mock_redis_fs.read_file.return_value = json.dumps(cached_logo)
    
    agent = LogoAgent()
    result = await agent.run(
        company_name="Cached Company",
        industry="technology",
        use_cache=True
    )
    
    assert result["cached"] is True
    assert result["logo_url"] == "https://cached.com/logo.png"
    
    # DALL-E should NOT be called when cached
    mock_dalle_provider.generate_logo.assert_not_called()


@pytest.mark.asyncio
async def test_logo_agent_fallback_on_error(mock_dalle_provider, mock_redis_fs):
    """Test fallback placeholder when DALL-E fails"""
    mock_dalle_provider.generate_logo.side_effect = Exception("DALL-E API error")
    
    agent = LogoAgent()
    result = await agent.run(
        company_name="Failed Company",
        industry="technology"
    )
    
    assert result is not None
    assert result["logo_url"] == agent.FALLBACK_LOGO_URL
    assert result["metadata"]["fallback"] is True
    assert "error" in result["metadata"]


@pytest.mark.asyncio
async def test_logo_agent_cache_write(mock_dalle_provider, mock_redis_fs):
    """Test logo caching after generation"""
    agent = LogoAgent()
    
    await agent.run(
        company_name="Cache Test",
        industry="technology",
        use_cache=True
    )
    
    # Verify cache write was called
    mock_redis_fs.write_file.assert_called_once()
    call_kwargs = mock_redis_fs.write_file.call_args.kwargs
    assert call_kwargs["ttl"] == 86400  # 24 hours


@pytest.mark.asyncio
async def test_logo_agent_no_cache(mock_dalle_provider, mock_redis_fs):
    """Test logo generation with caching disabled"""
    agent = LogoAgent()
    
    await agent.run(
        company_name="No Cache",
        industry="technology",
        use_cache=False
    )
    
    # Cache should not be read or written
    mock_redis_fs.read_file.assert_not_called()
    mock_redis_fs.write_file.assert_not_called()
    
    # DALL-E should still be called
    mock_dalle_provider.generate_logo.assert_called_once()
