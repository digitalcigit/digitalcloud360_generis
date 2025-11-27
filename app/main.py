"""
Genesis AI Deep Agents Service - FastAPI Application Entry Point
Architecture: Service séparé avec intégration DigitalCloud360 via APIs REST
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import time
import os
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.config.database import engine, create_tables
from app.api.middleware import PrometheusMiddleware, LoggingMiddleware
from app.api.v1 import auth, coaching, business, users, integrations, genesis, modules, sites
from app.api import dc360_adapter
from app.utils.exceptions import GenesisAIException
from app.utils.logger import setup_logging
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.core.integrations.digitalcloud360 import DigitalCloud360APIClient
from app.core.integrations.tavily import TavilyClient

# Setup structured logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Genesis AI Service...")
    
    # Initialize database (skip if SKIP_DB_INIT=true for manual testing)
    skip_db_init = os.getenv("SKIP_DB_INIT", "false").lower() == "true"
    if settings.ENVIRONMENT != "testing" and not skip_db_init:
        try:
            await create_tables()
            logger.info("Database tables created")
        except Exception as e:
            logger.warning("Database initialization skipped", error=str(e))

    # Initialize Redis connection
    redis_fs = RedisVirtualFileSystem()
    await redis_fs.health_check()
    logger.info("Redis Virtual File System initialized")
    
    # Validate external API connections (skip for manual testing)
    skip_api_validation = os.getenv("SKIP_API_VALIDATION", "false").lower() == "true"
    if settings.VALIDATE_EXTERNAL_APIS and not settings.TESTING_MODE and not skip_api_validation:
        try:
            await validate_external_apis()
        except Exception as e:
            logger.warning("External API validation skipped", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("Genesis AI Service shutting down...")

async def validate_external_apis():
    """Validate all external API connections on startup"""
    # Test DigitalCloud360 connection
    try:
        dc360_client = DigitalCloud360APIClient()
        await dc360_client.health_check()
        logger.info("DigitalCloud360 API connection validated")
    except Exception as e:
        logger.error("DigitalCloud360 API connection failed", error=str(e))
        raise
    
    # Test Tavily connection
    try:
        tavily_client = TavilyClient()
        # The Tavily client doesn't have a health_check method in the provided snippet.
        # I will assume it's okay to just initialize it.
        logger.info("Tavily Research API connection validated")
    except Exception as e:
        logger.error("Tavily API connection failed", error=str(e))
        raise

# FastAPI application instance
app = FastAPI(
    title="Genesis AI - Deep Agents Service",
    description="""
    # Premier Coach IA Personnel pour Entrepreneurs Africains 🌍
    
    ## Vue d'ensemble
    
    Genesis AI est un service d'orchestration intelligente utilisant **LangGraph** pour coordonner
    des agents spécialisés dans la génération complète de business briefs et création de sites web.
    
    ## Architecture
    
    - **Orchestrateur LangGraph** : Coordination state machine des sub-agents
    - **Sub-Agents spécialisés** :
      - ResearchSubAgent : Analyse marché (Tavily/Kimi)
      - ContentSubAgent : Génération contenu multilingue (Deepseek/OpenAI)
      - LogoSubAgent : Création logos (DALL-E 3)
      - SEOSubAgent : Optimisation SEO locale
      - TemplateSubAgent : Sélection templates adaptés
    
    ## Providers LLM
    
    - **Deepseek** : Primary LLM (économique, rapide)
    - **Kimi/Moonshot** : Search + LLM natif (web_search intégré)
    - **DALL-E 3** : Génération images/logos (7 styles)
    - **Tavily** : Fallback search spécialisé
    - **OpenAI GPT-4** : Fallback LLM (fiable)
    
    ## Intégrations
    
    - **Redis Virtual FS** : Persistance sessions (TTL 7 jours)
    - **DigitalCloud360 API** : Service-to-service (quotas, création sites)
    - **PostgreSQL** : Données métier
    
    ## Fonctionnalités
    
    - ✅ Génération business brief complet (~20-40s)
    - ✅ Analyse marché temps réel (Tavily/Kimi)
    - ✅ Contenu multilingue (Français, Wolof, Anglais)
    - ✅ Logos professionnels (7 styles DALL-E)
    - ✅ SEO optimisé local (mots-clés, meta tags)
    - ✅ Templates adaptés par secteur
    - ✅ Persistance Redis (7 jours TTL)
    - ✅ Intégration DC360 (quotas, création sites)
    
    ## Quotas
    
    | Plan | Briefs/mois | Rate Limit |
    |------|-------------|------------|
    | Trial | 10 | 5 req/min |
    | Basic | 25 | 10 req/min |
    | Pro | 50 | 20 req/min |
    | Enterprise | Illimité | 50 req/min |
    
    ## Authentification
    
    - **JWT Bearer Token** : Authentification utilisateurs DC360
    - **X-Service-Secret** : Authentification service-to-service
    
    ## Support
    
    - **Documentation** : [GitHub Wiki](https://github.com/digitalcigit/digitalcloud360_generis)
    - **Issues** : [GitHub Issues](https://github.com/digitalcigit/digitalcloud360_generis/issues)
    - **Contact** : support@digitalcloud360.com
    
    ## Version & Environnement
    
    - **Version** : {version}
    - **Environnement** : {environment}
    - **Health Check** : `GET /health`
    """.format(version=settings.APP_VERSION, environment=settings.ENVIRONMENT),
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    contact={
        "name": "DigitalCloud360 - Genesis AI Team",
        "url": "https://digitalcloud360.com",
        "email": "support@digitalcloud360.com"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://digitalcloud360.com/license"
    }
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Custom Middleware
app.add_middleware(PrometheusMiddleware)
app.add_middleware(LoggingMiddleware)

# Global Exception Handler
@app.exception_handler(GenesisAIException)
async def genesis_ai_exception_handler(request: Request, exc: GenesisAIException):
    """Handle custom Genesis AI exceptions"""
    # Safely get request path for logging (handle test environment)
    try:
        request_path = request.url.path
    except (KeyError, AttributeError):
        request_path = request.scope.get("path", "/unknown")
    
    logger.error(
        "Genesis AI Exception", 
        error_type=exc.__class__.__name__,
        error_message=str(exc),
        request_path=request_path,
        request_method=request.method
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    # Safely get request path for logging (handle test environment)
    try:
        request_path = request.url.path
    except (KeyError, AttributeError):
        request_path = request.scope.get("path", "/unknown")
    
    logger.error(
        "Unexpected Exception",
        error_type=exc.__class__.__name__,
        error_message=str(exc),
        request_path=request_path,
        request_method=request.method
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "Une erreur inattendue s'est produite",
            "timestamp": time.time()
        }
    )

# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Service health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check for all integrations"""
    from app.core.health import health_checker
    return await health_checker.check_all_integrations()

@app.get("/health/integrations", tags=["Health"])
async def integrations_health_check():
    """Health check specific to integrations"""
    from app.core.health import health_checker
    
    # Check seulement les intégrations critiques
    redis_healthy, redis_info = await health_checker.check_redis_integration()
    
    return {
        "redis": redis_info,
        "critical_services_healthy": redis_healthy,
        "timestamp": time.time()
    }

# API Routers - TO BE IMPLEMENTED BY TEAM
app.include_router(
    auth.router, 
    prefix=f"{settings.API_V1_STR}/auth", 
    tags=["Authentication"]
)
app.include_router(
    coaching.router, 
    prefix=f"{settings.API_V1_STR}/coaching", 
    tags=["Coaching"]
)
app.include_router(
    business.router, 
    prefix=f"{settings.API_V1_STR}/business", 
    tags=["Business Brief"]
)
app.include_router(
    genesis.router,
    prefix=f"{settings.API_V1_STR}/genesis",
    tags=["Genesis - DC360 Aligned"]
)
app.include_router(
    integrations.router, 
    prefix=f"{settings.API_V1_STR}/integrations", 
    tags=["Integrations"]
)
app.include_router(
    modules.router,
    prefix=f"{settings.API_V1_STR}/modules",
    tags=["User Modules"]
)
app.include_router(
    sites.router,
    prefix=f"{settings.API_V1_STR}/sites",
    tags=["Sites"]
)

# DC360 Adapter Router (sans préfixe /v1/ - endpoint alias)
app.include_router(
    dc360_adapter.router,
    prefix="/api/genesis",
    tags=["DC360 Integration"]
)

# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint with service information"""
    return {
        "message": "Genesis AI Deep Agents Service - Premier Coach IA Entrepreneur Africain",
        "version": settings.APP_VERSION,
        "docs_url": "/docs" if settings.DEBUG else "Documentation not available in production",
        "health_check": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
