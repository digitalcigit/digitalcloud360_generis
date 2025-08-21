# 🤖 WORK ORDER - Phase 2: Sub-Agents Spécialisés Genesis AI

**WO-002 | Date :** 20 août 2025  
**Assigné à :** TRAE (IA Senior Dev)  
**Priorité :** 🟢 **NORMALE** - Suite logique après succès Phase 1  
**Durée estimée :** 4-6 semaines  
**Objectif :** Implémenter les 5 Sub-Agents spécialisés et orchestrateur LangGraph

---

## 🎯 **Contexte et Objectif**

### **État Actuel - Phase 1 ✅ COMPLÉTÉE**
- Infrastructure FastAPI production-ready
- Authentification JWT fonctionnelle
- Coaching 5 étapes opérationnel (Vision → Offre)
- Persistance Redis + PostgreSQL
- Containerisation Docker stable

### **Objectif Phase 2**
Transformer Genesis AI en système complet : **Coaching → Génération automatique site web**

**Workflow cible :**
1. Entrepreneur complète coaching 5 étapes
2. Orchestrateur déclenche 5 Sub-Agents parallèles
3. Génération brief business complet
4. Création site web automatique DigitalCloud360

---

## 📋 **Tasks à Réaliser**

### **Phase 2A : Intégrations Core (Semaine 1-2)**

#### **🔥 Priorité Absolue : Réparer Imports Main.py**
**Problème identifié :**
```python
# app/main.py lignes 34, 49-50 - Imports inexistants
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.core.integrations.digitalcloud360 import DigitalCloud360APIClient
from app.core.integrations.tavily import TavilyClient
```

**Task 2A.1 : Créer Redis Virtual File System**
```bash
# Créer structure
mkdir -p app/core/integrations

# Fichier : app/core/integrations/__init__.py
touch app/core/integrations/__init__.py

# Fichier : app/core/integrations/redis_fs.py
# Template : Utiliser spécifications existantes
```

**Implementation :**
```python
# app/core/integrations/redis_fs.py
import redis.asyncio as redis
import json
from typing import Dict, Any, Optional, List
import structlog
from app.config.settings import settings

logger = structlog.get_logger()

class RedisVirtualFileSystem:
    """Virtual File System Redis pour sessions coaching persistantes"""
    
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
    
    async def health_check(self) -> bool:
        """Vérifier connexion Redis"""
        try:
            await self.redis.ping()
            logger.info("Redis Virtual File System healthy")
            return True
        except Exception as e:
            logger.error("Redis connection failed", error=str(e))
            return False
    
    async def write_session(self, session_id: str, data: Dict[str, Any], ttl: int = 7200) -> bool:
        """Écrire session coaching (TTL 2h par défaut)"""
        # Implementation complète selon spécifications
    
    async def read_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Lire session coaching"""
        # Implementation complète
    
    async def list_user_sessions(self, user_id: int) -> List[str]:
        """Lister sessions utilisateur"""
        # Implementation complète
```

**Task 2A.2 : Créer DigitalCloud360 API Client**
```python
# app/core/integrations/digitalcloud360.py
import httpx
from typing import Dict, Any, Optional
import structlog
from app.config.settings import settings

class DigitalCloud360APIClient:
    """Client API DigitalCloud360 pour intégration service-to-service"""
    
    def __init__(self):
        self.base_url = settings.DIGITALCLOUD360_API_URL
        self.service_secret = settings.DIGITALCLOUD360_SERVICE_SECRET
    
    async def health_check(self) -> bool:
        """Vérifier connexion DigitalCloud360 API"""
        # Implementation avec retry logic
    
    async def create_website(self, business_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Créer site web depuis brief business"""
        # Implementation complète selon spécifications API
    
    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer profil utilisateur DigitalCloud360"""
        # Implementation service-to-service auth
```

**Task 2A.3 : Créer Tavily API Client**
```python
# app/core/integrations/tavily.py
from tavily import TavilyClient as TavilySDK
from typing import Dict, Any, List
import structlog
from app.config.settings import settings

class TavilyClient:
    """Client Tavily pour recherche marché africain"""
    
    def __init__(self):
        self.client = TavilySDK(api_key=settings.TAVILY_API_KEY)
    
    async def search_market(self, query: str, location: str = "Africa") -> List[Dict[str, Any]]:
        """Recherche marché avec spécialisation Afrique"""
        # Implementation avec fallback si API fail
    
    async def analyze_competitors(self, business_sector: str, location: str) -> Dict[str, Any]:
        """Analyse concurrence locale"""
        # Implementation selon spécifications
```

### **Phase 2B : Sub-Agents Spécialisés (Semaine 2-4)**

#### **Task 2B.1 : Research Sub-Agent**
**Template :** `SUB_AGENTS_IMPLEMENTATIONS.py` (lignes complètes disponibles)  
**Fichier :** `app/core/deep_agents/sub_agents/research.py`

```python
# Structure obligatoire :
mkdir -p app/core/deep_agents/sub_agents

class ResearchSubAgent:
    """Sub-Agent spécialisé analyse marché africain"""
    
    async def analyze_market(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse marché complet avec Tavily API"""
        # Copier implémentation de SUB_AGENTS_IMPLEMENTATIONS.py
        # Adapter pour intégration TavilyClient
        
    async def research_competitors(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recherche concurrence locale"""
        
    async def market_opportunities(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identification opportunités marché"""
```

#### **Task 2B.2 : Content Sub-Agent** 
**Fichier :** `app/core/deep_agents/sub_agents/content.py`

```python
class ContentSubAgent:
    """Sub-Agent génération contenu multilingue"""
    
    async def generate_website_content(self, business_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Génération contenu site web complet"""
        # Template dans SUB_AGENTS_IMPLEMENTATIONS.py
        
    async def generate_seo_content(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Génération contenu optimisé SEO"""
        
    async def adapt_cultural_content(self, content: Dict[str, Any], location: str) -> Dict[str, Any]:
        """Adaptation culturelle contenu"""
```

#### **Task 2B.3 : Logo Sub-Agent**
**Fichier :** `app/core/deep_agents/sub_agents/logo.py`

```python
class LogoSubAgent:
    """Sub-Agent création identité visuelle LogoAI"""
    
    async def create_logo_identity(self, business_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Génération logo + palette couleurs"""
        # Intégration LogoAI API
        
    async def generate_brand_guidelines(self, logo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Génération guidelines marque"""
```

#### **Task 2B.4-5 : SEO + Template Sub-Agents**
**Fichiers :** `app/core/deep_agents/sub_agents/seo.py` + `template.py`

```python
# SEO Sub-Agent - Optimisation locale
class SEOSubAgent:
    async def optimize_local_seo(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimisation SEO marché local africain"""

# Template Sub-Agent - Sélection intelligente  
class TemplateSubAgent:
    async def select_optimal_template(self, business_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Sélection template selon secteur activité"""
```

### **Phase 2C : Orchestrateur LangGraph (Semaine 4-5)**

#### **Task 2C.1 : Orchestrateur Deep Agent**
**Template :** `ORCHESTRATEUR_DEEP_AGENT.py` (318 lignes code complet)  
**Fichier :** `app/core/deep_agents/orchestrator.py`

**Implementation :**
```python
# Copier-coller ORCHESTRATEUR_DEEP_AGENT.py et adapter :

from langgraph import StateGraph, CompiledGraph, END
from typing import TypedDict, List, Dict, Any

class GenesisAIState(TypedDict):
    """État centralisé Deep Agent"""
    session_id: str
    user_id: int
    current_step: str
    business_brief: Dict[str, Any] 
    sub_agents_results: Dict[str, Any]
    # ... autres champs selon template

class GenesisDeepAgentOrchestrator:
    """Orchestrateur principal LangGraph"""
    
    def __init__(self):
        # Initialisation tous sub-agents
        self.research_agent = ResearchSubAgent()
        self.content_agent = ContentSubAgent()
        # ... autres agents
        
    async def orchestrate_sub_agents(self, coaching_session: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestration parallèle 5 sub-agents"""
        # Implementation selon template ORCHESTRATEUR_DEEP_AGENT.py
```

### **Phase 2D : Intégration API Business (Semaine 5-6)**

#### **Task 2D.1 : Remplacer Placeholders business.py**
**Fichier :** `app/api/v1/business.py`

```python
# Remplacer tous les "raise HTTPException 501" par vraies implémentations :

@router.post("/brief/generate", response_model=BusinessBriefResponse)
async def generate_business_brief(request: BusinessBriefRequest):
    """VRAIE implémentation orchestrateur sub-agents"""
    orchestrator = GenesisDeepAgentOrchestrator()
    result = await orchestrator.orchestrate_sub_agents(request.coaching_results)
    # Retourner vrais résultats

@router.get("/subagents/{session_id}/results")
async def get_subagent_results(session_id: str):
    """VRAIE récupération résultats sub-agents"""
    # Implementation avec RedisVirtualFileSystem

@router.post("/website/create")  
async def create_website_from_brief(brief_id: str):
    """VRAIE création site DigitalCloud360"""
    dc360_client = DigitalCloud360APIClient()
    result = await dc360_client.create_website(business_brief)
    # Retourner URL site créé
```

---

## ✅ **Critères de Validation**

### **Phase 2A - Intégrations (Semaine 1-2)**
- [ ] `docker-compose up` démarre sans erreur import
- [ ] `curl localhost:8002/health` → 200 OK  
- [ ] Redis Virtual File System opérationnel
- [ ] Connexions APIs externes validées

### **Phase 2B - Sub-Agents (Semaine 2-4)**
- [ ] 5 Sub-Agents implémentés et testables
- [ ] Research Agent → Analyse marché fonctionnelle
- [ ] Content Agent → Génération contenu multilingue
- [ ] Logo Agent → Création identité visuelle
- [ ] SEO Agent → Optimisation locale
- [ ] Template Agent → Sélection intelligente

### **Phase 2C - Orchestrateur (Semaine 4-5)**
- [ ] GenesisDeepAgentOrchestrator opérationnel
- [ ] LangGraph workflow exécution parallèle
- [ ] Business brief génération complète
- [ ] State management Redis persistant

### **Phase 2D - API Business (Semaine 5-6)**
- [ ] POST `/api/v1/business/brief/generate` → Business brief réel
- [ ] GET `/api/v1/business/subagents/{id}/results` → Résultats sub-agents
- [ ] POST `/api/v1/business/website/create` → Site web créé DigitalCloud360

---

## 📊 **Livrables Attendus**

### **Architecture Technique**
1. ✅ Intégrations core (Redis FS, DC360 API, Tavily)
2. ✅ 5 Sub-Agents spécialisés fonctionnels
3. ✅ Orchestrateur LangGraph Deep Agents
4. ✅ APIs business endpoints opérationnels

### **Fonctionnalités Business**
1. ✅ Workflow complet : Coaching → Site web automatique
2. ✅ Génération brief business avec sub-agents
3. ✅ Création site web DigitalCloud360 intégrée
4. ✅ Performance < 45 minutes workflow total

### **Tests et Validation**
1. ✅ Tests automatisés sub-agents
2. ✅ Tests intégration bout en bout
3. ✅ Validation performance workflow
4. ✅ Monitoring et logs structurés

---

## 🎯 **Templates et Ressources**

### **Code Templates Disponibles (Copier-Coller)**
- **`SUB_AGENTS_IMPLEMENTATIONS.py`** → Implémentations complètes 5 sub-agents
- **`ORCHESTRATEUR_DEEP_AGENT.py`** → Orchestrateur LangGraph complet (318 lignes)
- **`API_SCHEMAS_COMPLETS.py`** → Types Pydantic exacts
- **`PROMPTS_COACHING_METHODOLOGIE.py`** → Base connaissances coaching

### **Documentation Référence**
- **`GUIDE_WORKFLOW_DEVELOPPEMENT_IA.md`** → Étapes précises Phase 2
- **`ARCHITECTURE_DECISION_RECORD.md`** → Justifications techniques
- **Docker configs** → Production-ready containers

---

## 🚨 **Points d'Attention Critiques**

### **Performance**
- Sub-Agents exécution **parallèle** (pas séquentielle)
- Timeout APIs externes : 30s max par agent
- Cache Redis résultats sub-agents (éviter re-calcul)

### **Sécurité**  
- Service-to-service auth DigitalCloud360
- API keys environnement uniquement
- Validation input utilisateur strict

### **Robustesse**
- Fallback mechanisms si APIs externes fail
- Retry logic avec backoff exponentiel  
- Error handling gracieux sans crash application

---

## 💡 **Démarrage Recommandé TRAE**

### **Semaine 1 - Quick Wins**
1. **Jour 1-2** : Réparer imports main.py (redis_fs.py, digitalcloud360.py, tavily.py)
2. **Jour 3-5** : Implémenter Research Sub-Agent (copier template)

### **Validation Continue**
```bash
# Test après chaque composant
docker-compose up -d
curl localhost:8002/health
pytest tests/test_sub_agents/ -v
```

---

**🎯 Objectif Final : Transformer Genesis AI en système révolutionnaire de coaching IA → création site web automatique pour entrepreneurs africains !**

**Status Attendu : 🟢 Sub-Agents Phase 2 complète = Genesis AI MVP fonctionnel**
