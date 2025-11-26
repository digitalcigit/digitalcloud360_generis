"""Application settings with environment variable loading"""

from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional
import secrets

class Settings(BaseSettings):
    """Application settings with environment variable loading"""
    
    # Application
    APP_NAME: str = "genesis-ai-service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "genesis_ai_user"
    POSTGRES_PASSWORD: str = "genesis_ai_password"  
    POSTGRES_DB: str = "genesis_ai_db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None
    TEST_DATABASE_URL: Optional[str] = None
    
    @field_validator("DATABASE_URL", mode='before')
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        """Construct database URL from components - PostgreSQL only"""
        if isinstance(v, str) and v:
            return v
        
        # Configuration par défaut PostgreSQL pour développement
        return "postgresql+asyncpg://genesis_user:your_secure_password_here@localhost:5435/genesis_db"

    @field_validator("TEST_DATABASE_URL", mode='before') 
    @classmethod
    def assemble_test_db_connection(cls, v: Optional[str]) -> str:
        """Construct test database URL from components - PostgreSQL only"""
        if isinstance(v, str) and v:
            return v
        # Utilise test-db pour Docker, localhost:5433 pour tests locaux
        return "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"
    
    # Redis Configuration
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_GENESIS_AI_DB: int = 0
    REDIS_SESSION_TTL: int = 7200  # 2 hours
    
    # DigitalCloud360 Integration
    # En développement local: DC360 tourne sur http://localhost:8000 (Docker)
    # En production: https://api.digitalcloud360.ci
    DIGITALCLOUD360_API_URL: str = "http://localhost:8000"
    DIGITALCLOUD360_SERVICE_SECRET: str = "change-me-in-production"
    DIGITALCLOUD360_TIMEOUT: int = 30
    
    # Genesis Service Secret (pour authentification service-to-service)
    # Doit être identique côté Genesis et DC360
    GENESIS_SERVICE_SECRET: str = "change-me-in-production"
    
    # AI Services - Sprint 2 Multi-Provider Architecture
    # LLM Providers
    DEEPSEEK_API_KEY: str = "your-deepseek-key"
    KIMI_API_KEY: str = "your-kimi-key"  # Moonshot AI
    OPENAI_API_KEY: str = "your-openai-key"
    ANTHROPIC_API_KEY: str = "your-anthropic-key"
    GOOGLE_API_KEY: Optional[str] = None  # Optional - Gemini
    
    # Search Providers
    TAVILY_API_KEY: str = "your-tavily-key"
    
    # Provider Configuration
    PRIMARY_LLM_PROVIDER: str = "deepseek"  # deepseek|openai|anthropic
    PRIMARY_SEARCH_PROVIDER: str = "tavily"  # tavily|kimi
    ENABLE_PROVIDER_FALLBACK: bool = True
    
    # Provider Base URLs
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    KIMI_BASE_URL: str = "https://api.moonshot.cn"
    TAVILY_BASE_URL: str = "https://api.tavily.com"
    
    # Security & CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080"
    ]
    
    # Monitoring
    PROMETHEUS_PORT: int = 8001
    SENTRY_DSN: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    TESTING_MODE: bool = False
    
    # Health Checks & Validation
    STRICT_HEALTH_CHECKS: bool = False
    VALIDATE_EXTERNAL_APIS: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_provider_api_keys(self) -> dict:
        """
        Construit dict API keys pour ProviderFactory
        
        Returns:
            Dict mapping provider name → API key
            
        Usage:
            factory = ProviderFactory(api_keys=settings.get_provider_api_keys())
        """
        api_keys = {}
        
        # LLM Providers
        if self.DEEPSEEK_API_KEY and not self.DEEPSEEK_API_KEY.startswith("your-"):
            api_keys["deepseek"] = self.DEEPSEEK_API_KEY
        
        if self.KIMI_API_KEY and not self.KIMI_API_KEY.startswith("your-"):
            api_keys["kimi"] = self.KIMI_API_KEY
        
        if self.OPENAI_API_KEY and not self.OPENAI_API_KEY.startswith("your-"):
            api_keys["openai"] = self.OPENAI_API_KEY
            api_keys["dalle-3"] = self.OPENAI_API_KEY  # DALL-E utilise OpenAI key
        
        if self.ANTHROPIC_API_KEY and not self.ANTHROPIC_API_KEY.startswith("your-"):
            api_keys["anthropic"] = self.ANTHROPIC_API_KEY
        
        if self.GOOGLE_API_KEY:
            api_keys["google"] = self.GOOGLE_API_KEY
        
        # Search Providers
        if self.TAVILY_API_KEY and not self.TAVILY_API_KEY.startswith("your-"):
            api_keys["tavily"] = self.TAVILY_API_KEY
        
        return api_keys

# Global settings instance
settings = Settings()

