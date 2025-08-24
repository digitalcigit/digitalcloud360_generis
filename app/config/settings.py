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
    DIGITALCLOUD360_API_URL: str = "https://api.digitalcloud360.com"
    DIGITALCLOUD360_SERVICE_SECRET: str = "change-me-in-production"
    DIGITALCLOUD360_TIMEOUT: int = 30
    
    # AI Services
    OPENAI_API_KEY: str = "your-openai-key"
    ANTHROPIC_API_KEY: str = "your-anthropic-key"
    TAVILY_API_KEY: str = "your-tavily-key"
    LOGOAI_API_KEY: str = "your-logoai-key"
    
    # External Services URLs
    LOGOAI_BASE_URL: str = "https://api.logoai.com"
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

# Global settings instance
settings = Settings()

