# Configuration Management

<cite>
**Referenced Files in This Document**   
- [settings.py](file://app/config/settings.py#L7-L78)
- [database.py](file://app/config/database.py#L1-L43)
- [redis.py](file://app/config/redis.py#L1-L15)
- [main.py](file://app/main.py#L35-L73)
- [digitalcloud360.py](file://app/core/integrations/digitalcloud360.py#L1-L82)
- [tavily.py](file://app/core/integrations/tavily.py#L1-L43)
- [openai.py](file://app/core/integrations/openai.py#L1-L44)
- [security.py](file://app/core/security.py#L1-L46)
- [docker-compose.yml](file://docker-compose.yml#L1-L167)
</cite>

## Table of Contents
1. [Configuration Management](#configuration-management)
2. [Settings Hierarchy and Environment Loading](#settings-hierarchy-and-environment-loading)
3. [Database Configuration](#database-configuration)
4. [Redis Configuration](#redis-configuration)
5. [AI and External Service Integrations](#ai-and-external-service-integrations)
6. [Security and CORS Settings](#security-and-cors-settings)
7. [Environment-Specific Configurations](#environment-specific-configurations)
8. [Connection String Formats and Validation](#connection-string-formats-and-validation)
9. [Timeout and Retry Configurations](#timeout-and-retry-configurations)
10. [Environment Setup and Docker Integration](#environment-setup-and-docker-integration)
11. [Security Best Practices for Secrets Management](#security-best-practices-for-secrets-management)
12. [Customization for Deployment Scenarios](#customization-for-deployment-scenarios)

## Settings Hierarchy and Environment Loading

The configuration system is built on **Pydantic BaseSettings**, enabling robust environment variable loading and type validation. The `Settings` class in `settings.py` serves as the central configuration hub, automatically loading values from environment variables and a `.env` file.

Key features:
- **Environment file support**: Loads from `.env` via `env_file = ".env"`
- **Case sensitivity**: `case_sensitive = True` ensures exact variable name matching
- **Field validation**: Uses `@field_validator` to dynamically construct values
- **Default values**: Provides sensible defaults for local development

The global `settings` instance allows any module to access configuration through simple imports.

```python
from app.config.settings import settings
```

This pattern ensures consistent, type-safe access to configuration across the entire application.

**Section sources**
- [settings.py](file://app/config/settings.py#L7-L78)

## Database Configuration

Database settings are managed through structured environment variables that combine to form a complete connection URL. The system uses **asyncpg** with **SQLAlchemy 2.0-style async engines** for high-performance database operations.

### Configuration Options
:POSTGRES_SERVER: Hostname for PostgreSQL server (default: `localhost`)
:POSTGRES_USER: Database username (default: `genesis_ai_user`)
:POSTGRES_PASSWORD: Database password (default: `genesis_ai_password`)
:POSTGRES_DB: Database name (default: `genesis_ai_db`)
:POSTGRES_PORT: Port number (default: `5432`)
:DATABASE_URL: Full connection string (auto-assembled if not provided)
:TEST_DATABASE_URL: Connection string for testing database

### Connection Management
The database engine is configured with:
- **Echo logging**: Enabled when `DEBUG=True`
- **Pool pre-ping**: Verifies connections before use
- **Pool recycle**: Recycles connections every 300 seconds

```mermaid
flowchart TD
A["Application Startup"] --> B["Load Settings from Environment"]
B --> C["Construct DATABASE_URL"]
C --> D["Create Async Engine"]
D --> E["Initialize Session Factory"]
E --> F["Create Database Tables"]
F --> G["Ready for Requests"]
```

**Diagram sources**
- [settings.py](file://app/config/settings.py#L7-L78)
- [database.py](file://app/config/database.py#L1-L43)

**Section sources**
- [settings.py](file://app/config/settings.py#L7-L78)
- [database.py](file://app/config/database.py#L1-L43)

## Redis Configuration

Redis is used for session storage and virtual file system operations. The configuration is minimal but effective, using a standard Redis URL format.

### Configuration Options
:REDIS_URL: Complete Redis connection URL (default: `redis://redis:6379/0`)
:REDIS_GENESIS_AI_DB: Database index to use (default: `0`)
:REDIS_SESSION_TTL: Session timeout in seconds (default: `7200` - 2 hours)

The Redis client is initialized asynchronously and includes health checking:

```python
async def get_redis_client():
    redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    if await redis_client.ping():
        return redis_client
```

This ensures the application verifies connectivity before using Redis.

**Section sources**
- [settings.py](file://app/config/settings.py#L7-L78)
- [redis.py](file://app/config/redis.py#L1-L15)

## AI and External Service Integrations

The system integrates with multiple AI and external services, each with dedicated configuration parameters.

### OpenAI Integration
:OPENAI_API_KEY: API key for OpenAI services
- Used by `OpenAIClient` for text generation
- Required at initialization
- Accessed via environment variable

### Tavily Integration
:TAVILY_API_KEY: API key for market research
:TAVILY_BASE_URL: Base URL for API calls (default: `https://api.tavily.com`)
- Used for African market research and competitor analysis
- Includes fallback behavior on failure

### LogoAI Integration
:LOGOAI_API_KEY: API key for logo generation
:LOGOAI_BASE_URL: Base URL for API calls (default: `https://api.logoai.com`)
- Currently implemented as a mock service
- Returns placeholder logo URLs

### DigitalCloud360 Integration
:DIGITALCLOUD360_API_URL: Base API URL (default: `https://api.digitalcloud360.com`)
:DIGITALCLOUD360_SERVICE_SECRET: Authentication secret
:DIGITALCLOUD360_TIMEOUT: Request timeout in seconds (default: `30`)

```mermaid
sequenceDiagram
participant App as Application
participant DC360 as DigitalCloud360
App->>App : Initialize Client
App->>DC360 : GET /health (with retry)
alt Healthy
DC360-->>App : 200 OK
App->>App : Mark as healthy
else Unhealthy
App->>App : Exponential backoff
App->>DC360 : Retry request
end
```

**Diagram sources**
- [digitalcloud360.py](file://app/core/integrations/digitalcloud360.py#L1-L82)
- [tavily.py](file://app/core/integrations/tavily.py#L1-L43)
- [openai.py](file://app/core/integrations/openai.py#L1-L44)

**Section sources**
- [digitalcloud360.py](file://app/core/integrations/digitalcloud360.py#L1-L82)
- [tavily.py](file://app/core/integrations/tavily.py#L1-L43)
- [openai.py](file://app/core/integrations/openai.py#L1-L44)
- [logoai.py](file://app/core/integrations/logoai.py#L1-L31)

## Security and CORS Settings

Security configuration includes JWT token management and CORS policy.

### JWT Configuration
:SECRET_KEY: Cryptographic key for token signing (auto-generated if not provided)
:ACCESS_TOKEN_EXPIRE_MINUTES: Token lifetime (default: `43200` - 30 days)

The system uses **HS256 algorithm** with **passlib bcrypt** for password hashing.

### CORS Configuration
:CORS_ORIGINS: List of allowed origins (default: `http://localhost:3000`, `http://localhost:8080`)
- Configured in FastAPI middleware
- Allows credentials and all headers/methods

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Section sources**
- [settings.py](file://app/config/settings.py#L7-L78)
- [security.py](file://app/core/security.py#L1-L46)
- [main.py](file://app/main.py#L100-L110)

## Environment-Specific Configurations

The system supports multiple environments through the `ENVIRONMENT` setting.

### Environment Modes
:ENVIRONMENT: Current environment (default: `development`)
:DEBUG: Debug mode flag (default: `False`)
:TESTING_MODE: Testing flag (default: `False`)
:LOG_LEVEL: Logging level (default: `INFO`)

### Environment Behaviors
- **Development**: Enables docs, debug mode, verbose logging
- **Testing**: Uses in-memory SQLite, skips external API validation
- **Production**: Disables docs, strict error handling, optimized logging

The test suite overrides settings for isolated testing:

```python
def get_settings_override() -> Settings:
    return Settings(
        TESTING_MODE=True,
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        ENVIRONMENT="testing"
    )
```

**Section sources**
- [settings.py](file://app/config/settings.py#L7-L78)
- [main.py](file://app/main.py#L35-L73)
- [tests/conftest.py](file://tests/conftest.py#L38-L80)

## Connection String Formats and Validation

Connection strings are constructed programmatically to ensure correctness.

### Database URL Construction
The `DATABASE_URL` is auto-assembled from component parts:

```python
@field_validator("DATABASE_URL", mode='before')
def assemble_db_connection(cls, v: Optional[str], values: "ValidationInfo") -> any:
    if isinstance(v, str):
        return v
    return f"postgresql+asyncpg://{values.data.get('POSTGRES_USER')}:{values.data.get('POSTGRES_PASSWORD')}@{values.data.get('POSTGRES_SERVER')}:{values.data.get('POSTGRES_PORT')}/{values.data.get('POSTGRES_DB')}"
```

This ensures consistent URL formatting across environments.

### Supported Formats
:Production: `postgresql+asyncpg://user:password@postgres:5432/genesis_db`
:Development: `postgresql+asyncpg://genesis_ai_user:genesis_ai_password@localhost:5432/genesis_ai_db`
:Testing: `sqlite+aiosqlite:///:memory:` (in-memory database)

**Section sources**
- [settings.py](file://app/config/settings.py#L7-L78)
- [database.py](file://app/config/database.py#L1-L43)

## Timeout and Retry Configurations

External service integrations include robust timeout and retry logic.

### DigitalCloud360 Retry Logic
- **Max retries**: 3 attempts
- **Exponential backoff**: 2^attempt seconds delay
- **Timeout**: 30 seconds per request
- **Health check**: Automatic validation at startup

```python
for attempt in range(self.max_retries):
    try:
        # API call
        break
    except Exception:
        if attempt < self.max_retries - 1:
            await asyncio.sleep(2 ** attempt)
```

### General Resilience
- All external calls use async HTTP clients
- Comprehensive error logging
- Graceful degradation when possible
- Critical failures halt application startup

**Section sources**
- [digitalcloud360.py](file://app/core/integrations/digitalcloud360.py#L1-L82)

## Environment Setup and Docker Integration

The system uses Docker and docker-compose for consistent environment management.

### .env File Setup
Create `.env` file with:
```
POSTGRES_PASSWORD=your_secure_password
GRAFANA_PASSWORD=your_grafana_password
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
LOGOAI_API_KEY=your_logoai_key
DIGITALCLOUD360_SERVICE_SECRET=your_secure_secret
```

### Docker Environment Injection
docker-compose.yml injects environment variables:

```yaml
environment:
  - TEST_DATABASE_URL=postgresql+asyncpg://test_user:test_password@test-db:5432/test_db
env_file:
  - .env
```

Service-specific configurations:
- **PostgreSQL**: Password via environment variable
- **Redis**: Configured with persistence and memory limits
- **API Service**: Mounts code volume for development

```mermaid
graph TB
A[".env File"] --> B["Docker Compose"]
B --> C["genesis-api"]
B --> D["postgres"]
B --> E["redis"]
C --> F["Application Settings"]
D --> G["Database Configuration"]
E --> H["Redis Configuration"]
```

**Diagram sources**
- [docker-compose.yml](file://docker-compose.yml#L1-L167)

**Section sources**
- [docker-compose.yml](file://docker-compose.yml#L1-L167)

## Security Best Practices for Secrets Management

The configuration system follows security best practices for managing sensitive data.

### Secret Handling
- **Never commit secrets**: Default values are safe for development
- **Environment variables**: Primary method for secret injection
- **.env file**: Git-ignored, used for local development
- **Docker secrets**: Supported through environment variable substitution

### Production Recommendations
1. Use secret management tools (Hashicorp Vault, AWS Secrets Manager)
2. Rotate API keys regularly
3. Restrict database user permissions
4. Use strong, randomly generated `SECRET_KEY`
5. Set `DIGITALCLOUD360_SERVICE_SECRET` to cryptographically secure value

### Sensitive Settings
:SECRET_KEY: Must be rotated in production
:DIGITALCLOUD360_SERVICE_SECRET: Should not be "change-me-in-production"
:OPENAI_API_KEY: Should have restricted permissions
:POSTGRES_PASSWORD: Database credentials should be complex

**Section sources**
- [settings.py](file://app/config/settings.py#L7-L78)

## Customization for Deployment Scenarios

The configuration system supports easy customization for different deployment scenarios.

### Development Customization
Set in `.env`:
```
DEBUG=true
LOG_LEVEL=DEBUG
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Production Customization
```
DEBUG=false
LOG_LEVEL=WARNING
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com
SECRET_KEY=your_strong_secret_key
SENTRY_DSN=https://your-sentry-dsn
```

### Testing Configuration
Automatically configured:
- In-memory SQLite database
- Testing mode enabled
- Isolated test database

### Custom Deployment Example
For staging environment:
```python
Settings(
    ENVIRONMENT="staging",
    DATABASE_URL="postgresql+asyncpg://user:pass@staging-db:5432/staging_db",
    REDIS_URL="redis://staging-redis:6379/0",
    LOG_LEVEL="INFO"
)
```

The flexible Pydantic settings model allows programmatic configuration for any deployment scenario.

**Section sources**
- [settings.py](file://app/config/settings.py#L7-L78)
- [main.py](file://app/main.py#L35-L73)
- [tests/conftest.py](file://tests/conftest.py#L38-L80)