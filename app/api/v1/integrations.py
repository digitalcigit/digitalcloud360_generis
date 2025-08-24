"""Integrations endpoints for Genesis AI Service"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.responses import SuccessResponse
from app.api.v1.dependencies import (
    get_current_user, 
    get_redis_vfs, 
    get_digitalcloud360_client,
    get_tavily_client
)
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.core.integrations.digitalcloud360 import DigitalCloud360APIClient
from app.core.integrations.tavily import TavilyClient
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import structlog

router = APIRouter()
logger = structlog.get_logger()

# Schemas pour la documentation Swagger

class HealthCheckResponse(BaseModel):
    """Réponse du health check d'un service"""
    service: str
    status: str  # "healthy" ou "unhealthy"
    response_time: Optional[float] = None
    error: Optional[str] = None

class AllHealthCheckResponse(BaseModel):
    """Réponse du health check global"""
    overall_status: str
    services: Dict[str, HealthCheckResponse]

class SearchRequest(BaseModel):
    """Requête de recherche Tavily"""
    query: str
    search_depth: Optional[str] = "basic"  # "basic" ou "deep"
    max_results: Optional[int] = 5
    include_domains: Optional[List[str]] = None
    exclude_domains: Optional[List[str]] = None

class SearchResponse(BaseModel):
    """Réponse de recherche Tavily"""
    query: str
    results: List[Dict[str, Any]]
    answer: Optional[str] = None
    total_results: int

class FileOperationRequest(BaseModel):
    """Requête d'opération sur fichier Redis FS"""
    path: str
    content: Optional[str] = None
    ttl: Optional[int] = None

class FileInfoResponse(BaseModel):
    """Informations sur un fichier Redis FS"""
    path: str
    exists: bool
    size: Optional[int] = None
    created_at: Optional[str] = None
    ttl: Optional[int] = None

class AgentRequest(BaseModel):
    """Requête de création d'agent DigitalCloud360"""
    name: str
    description: str
    capabilities: List[str]

class AgentResponse(BaseModel):
    """Réponse d'agent DigitalCloud360"""
    id: str
    name: str
    description: str
    status: str
    capabilities: List[str]

# Endpoints Health Checks

@router.get("/health", response_model=AllHealthCheckResponse)
async def check_all_integrations_health(
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs),
    dc360_client: DigitalCloud360APIClient = Depends(get_digitalcloud360_client),
    tavily_client: TavilyClient = Depends(get_tavily_client)
):
    """
    🏥 Vérifier l'état de santé de toutes les intégrations
    
    Effectue un health check complet de tous les services externes intégrés :
    - Redis Virtual File System
    - DigitalCloud360 API
    - Tavily Search API
    
    Retourne le statut détaillé de chaque service avec temps de réponse.
    """
    import time
    
    logger.info("Health check requested for all integrations", user_id=current_user.id)
    
    health_results = {}
    overall_healthy = True
    
    # Check Redis
    try:
        start_time = time.time()
        redis_healthy = await redis_fs.health_check()
        response_time = time.time() - start_time
        
        health_results["redis"] = HealthCheckResponse(
            service="redis",
            status="healthy" if redis_healthy else "unhealthy",
            response_time=response_time
        )
        if not redis_healthy:
            overall_healthy = False
    except Exception as e:
        health_results["redis"] = HealthCheckResponse(
            service="redis",
            status="unhealthy",
            error=str(e)
        )
        overall_healthy = False
    
    # Check DigitalCloud360
    try:
        start_time = time.time()
        dc360_healthy = await dc360_client.health_check()
        response_time = time.time() - start_time
        
        health_results["digitalcloud360"] = HealthCheckResponse(
            service="digitalcloud360",
            status="healthy" if dc360_healthy else "unhealthy",
            response_time=response_time
        )
        if not dc360_healthy:
            overall_healthy = False
    except Exception as e:
        health_results["digitalcloud360"] = HealthCheckResponse(
            service="digitalcloud360",
            status="unhealthy",
            error=str(e)
        )
        overall_healthy = False
    
    # Check Tavily
    try:
        start_time = time.time()
        tavily_healthy = await tavily_client.health_check()
        response_time = time.time() - start_time
        
        health_results["tavily"] = HealthCheckResponse(
            service="tavily",
            status="healthy" if tavily_healthy else "unhealthy",
            response_time=response_time
        )
        if not tavily_healthy:
            overall_healthy = False
    except Exception as e:
        health_results["tavily"] = HealthCheckResponse(
            service="tavily",
            status="unhealthy",
            error=str(e)
        )
        overall_healthy = False
    
    return AllHealthCheckResponse(
        overall_status="healthy" if overall_healthy else "unhealthy",
        services=health_results
    )

# Endpoints Tavily Search

@router.post("/tavily/search", response_model=SearchResponse)
async def search_with_tavily(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user),
    tavily_client: TavilyClient = Depends(get_tavily_client)
):
    """
    🔍 Effectuer une recherche web intelligente avec Tavily
    
    Utilise l'API Tavily pour effectuer une recherche web avancée avec :
    - Extraction de contenu intelligent
    - Résumé automatique des résultats
    - Filtrage par domaines
    - Contrôle de la profondeur de recherche
    
    **Paramètres :**
    - `query`: Termes de recherche
    - `search_depth`: "basic" (rapide) ou "deep" (approfondie)
    - `max_results`: Nombre maximum de résultats (1-10)
    - `include_domains`: Liste des domaines à inclure
    - `exclude_domains`: Liste des domaines à exclure
    """
    logger.info("Tavily search requested", 
               user_id=current_user.id, 
               query=request.query,
               search_depth=request.search_depth)
    
    try:
        search_kwargs = {
            "search_depth": request.search_depth,
            "max_results": request.max_results
        }
        
        if request.include_domains:
            search_kwargs["include_domains"] = request.include_domains
        if request.exclude_domains:
            search_kwargs["exclude_domains"] = request.exclude_domains
        
        results = await tavily_client.search(request.query, **search_kwargs)
        
        logger.info("Tavily search completed successfully", 
                   query=request.query,
                   results_count=len(results.get("results", [])))
        
        return SearchResponse(
            query=request.query,
            results=results.get("results", []),
            answer=results.get("answer"),
            total_results=len(results.get("results", []))
        )
        
    except Exception as e:
        logger.error("Tavily search failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/tavily/extract")
async def extract_content_from_url(
    url: str = Query(..., description="URL dont extraire le contenu"),
    current_user: dict = Depends(get_current_user),
    tavily_client: TavilyClient = Depends(get_tavily_client)
):
    """
    📄 Extraire le contenu principal d'une URL
    
    Utilise Tavily pour extraire et structurer le contenu principal d'une page web :
    - Titre de la page
    - Contenu textuel principal
    - Métadonnées (auteur, date de publication)
    - Nettoyage automatique du contenu
    """
    logger.info("Content extraction requested", user_id=current_user.id, url=url)
    
    try:
        content = await tavily_client.extract_content(url)
        
        logger.info("Content extraction completed", url=url)
        return content
        
    except Exception as e:
        logger.error("Content extraction failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content extraction failed: {str(e)}"
        )

# Endpoints Redis Virtual File System

@router.post("/redis-fs/write", response_model=SuccessResponse)
async def write_file_to_redis(
    request: FileOperationRequest,
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    """
    💾 Écrire un fichier dans le système de fichiers virtuel Redis
    
    Stocke du contenu dans Redis avec un chemin de fichier virtuel :
    - Stockage temporaire avec TTL optionnel
    - Organisation hiérarchique par chemins
    - Gestion automatique des métadonnées
    """
    logger.info("Redis FS write requested", 
               user_id=current_user.id, 
               path=request.path)
    
    try:
        if not request.content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content is required for write operation"
            )
        
        success = await redis_fs.write_file(request.path, request.content, request.ttl)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to write file to Redis"
            )
        
        logger.info("File written successfully to Redis FS", path=request.path)
        return SuccessResponse(message=f"File written successfully to {request.path}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Redis FS write failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Write operation failed: {str(e)}"
        )

@router.get("/redis-fs/read")
async def read_file_from_redis(
    path: str = Query(..., description="Chemin du fichier à lire"),
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    """
    📖 Lire un fichier depuis le système de fichiers virtuel Redis
    
    Récupère le contenu d'un fichier stocké dans Redis :
    - Accès par chemin de fichier virtuel
    - Retourne le contenu brut
    - Gestion automatique des fichiers expirés
    """
    logger.info("Redis FS read requested", user_id=current_user.id, path=path)
    
    try:
        content = await redis_fs.read_file(path)
        
        if content is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {path}"
            )
        
        logger.info("File read successfully from Redis FS", path=path)
        return {"path": path, "content": content}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Redis FS read failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Read operation failed: {str(e)}"
        )

@router.get("/redis-fs/info", response_model=FileInfoResponse)
async def get_file_info_from_redis(
    path: str = Query(..., description="Chemin du fichier"),
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    """
    ℹ️ Obtenir les informations d'un fichier Redis FS
    
    Récupère les métadonnées d'un fichier :
    - Existence du fichier
    - Taille en octets
    - Date de création
    - TTL restant
    """
    logger.info("Redis FS info requested", user_id=current_user.id, path=path)
    
    try:
        exists = await redis_fs.file_exists(path)
        
        if exists:
            info = await redis_fs.get_file_info(path)
            return FileInfoResponse(
                path=path,
                exists=True,
                size=info.get("size"),
                created_at=info.get("created_at"),
                ttl=info.get("ttl")
            )
        else:
            return FileInfoResponse(path=path, exists=False)
            
    except Exception as e:
        logger.error("Redis FS info failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Info operation failed: {str(e)}"
        )

@router.get("/redis-fs/list")
async def list_files_in_redis(
    prefix: str = Query("", description="Préfixe pour filtrer les fichiers"),
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    """
    📋 Lister les fichiers dans le système Redis FS
    
    Retourne la liste des fichiers avec un préfixe donné :
    - Filtrage par préfixe de chemin
    - Navigation hiérarchique
    - Liste complète ou filtrée
    """
    logger.info("Redis FS list requested", 
               user_id=current_user.id, 
               prefix=prefix)
    
    try:
        files = await redis_fs.list_files(prefix)
        
        logger.info("Files listed successfully", 
                   prefix=prefix, 
                   count=len(files))
        
        return {"prefix": prefix, "files": files, "count": len(files)}
        
    except Exception as e:
        logger.error("Redis FS list failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"List operation failed: {str(e)}"
        )

# Endpoints DigitalCloud360

@router.get("/digitalcloud360/agents")
async def list_digitalcloud360_agents(
    current_user: dict = Depends(get_current_user),
    dc360_client: DigitalCloud360APIClient = Depends(get_digitalcloud360_client)
):
    """
    🤖 Lister tous les agents DigitalCloud360
    
    Récupère la liste de tous les agents disponibles sur la plateforme :
    - Agents actifs et inactifs
    - Métadonnées complètes
    - Statut et capacités
    """
    logger.info("DigitalCloud360 agents list requested", user_id=current_user.id)
    
    try:
        agents = await dc360_client.list_agents()
        
        logger.info("Agents listed successfully", count=len(agents))
        return {"agents": agents, "count": len(agents)}
        
    except Exception as e:
        logger.error("DigitalCloud360 list agents failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )

@router.post("/digitalcloud360/agents", response_model=AgentResponse)
async def create_digitalcloud360_agent(
    request: AgentRequest,
    current_user: dict = Depends(get_current_user),
    dc360_client: DigitalCloud360APIClient = Depends(get_digitalcloud360_client)
):
    """
    ➕ Créer un nouvel agent DigitalCloud360
    
    Crée et configure un nouvel agent sur la plateforme :
    - Configuration des capacités
    - Définition du rôle et de la description
    - Activation automatique
    """
    logger.info("DigitalCloud360 agent creation requested", 
               user_id=current_user.id,
               agent_name=request.name)
    
    try:
        agent_data = request.dict()
        agent = await dc360_client.create_agent(agent_data)
        
        logger.info("Agent created successfully", 
                   agent_id=agent.get("id"),
                   agent_name=request.name)
        
        return AgentResponse(**agent)
        
    except Exception as e:
        logger.error("DigitalCloud360 create agent failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )

@router.get("/digitalcloud360/agents/{agent_id}", response_model=AgentResponse)
async def get_digitalcloud360_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user),
    dc360_client: DigitalCloud360APIClient = Depends(get_digitalcloud360_client)
):
    """
    🔍 Récupérer un agent DigitalCloud360 spécifique
    
    Obtient les détails complets d'un agent :
    - Configuration actuelle
    - Statut et métriques
    - Historique des performances
    """
    logger.info("DigitalCloud360 agent retrieval requested", 
               user_id=current_user.id,
               agent_id=agent_id)
    
    try:
        agent = await dc360_client.get_agent(agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent not found: {agent_id}"
            )
        
        logger.info("Agent retrieved successfully", agent_id=agent_id)
        return AgentResponse(**agent)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("DigitalCloud360 get agent failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}"
        )