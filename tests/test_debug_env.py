
import os
import pytest
from tests.conftest_profile import TEST_PROFILE_INFO

@pytest.mark.asyncio
async def test_debug_environment():
    print("\n=== DEBUG ENVIRONMENT ===")
    print(f"TEST_PROFILE env var: {os.getenv('TEST_PROFILE')}")
    print(f"Detected Profile: {TEST_PROFILE_INFO}")
    
    from app.config.settings import settings
    print(f"Settings DATABASE_URL: {settings.DATABASE_URL}")
    print(f"Settings TEST_DATABASE_URL: {settings.TEST_DATABASE_URL}")
    
    # Check what conftest_profile loaded
    import tests.conftest_profile as cp
    print(f"cp.test_env: {cp.test_env}")
    
    assert cp.test_env == "docker"
    assert "test-db:5432" in TEST_PROFILE_INFO["database_url"]
