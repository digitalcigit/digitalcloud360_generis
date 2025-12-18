---
title: "Work Order GEN-13 — Intégration LangGraph au Chat"
work_order_id: "WO-GEN-13"
date: "2025-12-18"
from: "Tech Lead Genesis AI (Cascade)"
to: "Senior Dev IA (Cascade Instance)"
branch: "feature/GEN-13-langgraph-chat"
priority: "🔴 HAUTE"
status: "ASSIGNÉ"
estimated_effort: "3 points (6-8h)"
tags: ["phase2", "langgraph", "chat", "orchestrator", "sprint6"]
---

# 📋 Work Order GEN-13 — Intégration LangGraph au Chat

## 🎯 Objectif

> **Remplacer la logique mock du endpoint `/api/v1/chat` par l'appel réel au LangGraph Orchestrator** avec les 5 sub-agents fonctionnels.

**Résultat attendu :** Quand l'utilisateur décrit son business dans le chat, le système exécute réellement les 5 agents IA et génère un site complet.

---

## 📂 Informations Branche

| Info | Valeur |
|------|--------|
| **Branche de travail** | `feature/GEN-13-langgraph-chat` |
| **Branche source** | `master` |
| **Commit de départ** | `bf3be307` |

```bash
# Pour démarrer
git fetch origin
git checkout feature/GEN-13-langgraph-chat
```

---

## 🐳 Environnement Containerisé

### Architecture Docker

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCKER NETWORK                            │
│              genesis_genesis-ai-network (172.32.0.0/16)      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ genesis-api  │  │ postgres     │  │ redis        │       │
│  │ :8000 → 8002 │  │ :5432 → 5435 │  │ :6379 → 6382 │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ frontend     │  │ test-db      │                         │
│  │ :3000 → 3002 │  │ :5432 → 5433 │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### Commandes de lancement

```bash
# Depuis c:\genesis

# Lancer l'environnement de dev (API + DB + Redis)
docker-compose up -d postgres redis genesis-api

# Vérifier que tout est healthy
docker ps --format "table {{.Names}}\t{{.Status}}"

# Logs de l'API en temps réel
docker logs -f genesis-api
```

### Ports exposés (hôte Windows)

| Service | Port Interne | Port Hôte | URL |
|---------|--------------|-----------|-----|
| Genesis API | 8000 | **8002** | `http://localhost:8002` |
| PostgreSQL | 5432 | **5435** | `localhost:5435` |
| Redis | 6379 | **6382** | `localhost:6382` |
| Frontend | 3000 | **3002** | `http://localhost:3002` |
| Test DB | 5432 | **5433** | `localhost:5433` |

### Variables d'environnement critiques

```env
# Dans docker-compose.yml pour genesis-api
DATABASE_URL=postgresql+asyncpg://genesis:genesis@postgres:5432/genesis_db
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=<from .env>
TAVILY_API_KEY=<from .env>
DEEPSEEK_API_KEY=<from .env>
```

---

## 📁 Fichiers à Modifier

### 1. `app/api/v1/chat.py` (PRINCIPAL)

**Emplacement :** `c:\genesis\app\api\v1\chat.py`

**État actuel (lignes 39-67) — MOCK à remplacer :**
```python
# MOCK LOGIC POUR TEST E2E :
# Si le message contient "site", on simule une génération réussie
if "site" in request.message.lower():
    brief_id = f"brief_{uuid.uuid4()}"
    brief_data = {
        "business_brief": {
            "business_name": "Mon Entreprise",
            "sector": "default",
            "services": [],
        },
    }
    # ... reste du mock
```

**Modification requise :**
1. Importer `LangGraphOrchestrator` depuis `app.core.orchestration.langgraph_orchestrator`
2. Importer `BriefToSiteTransformer` depuis `app.services.transformer`
3. Remplacer la logique mock par :
   - Extraction du business context depuis le message
   - Appel `orchestrator.run(orchestration_input)`
   - Transformation du résultat en `SiteDefinition` via le transformer
   - Sauvegarde en base de données
   - Retour de la réponse avec `site_data`

**Signature cible :**
```python
from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
from app.services.transformer import BriefToSiteTransformer
from app.api.v1.dependencies import get_orchestrator

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs),
    orchestrator: LangGraphOrchestrator = Depends(get_orchestrator),
):
    # ... implémentation réelle
```

### 2. `app/api/v1/dependencies.py`

**Emplacement :** `c:\genesis\app\api\v1\dependencies.py`

**État actuel (ligne 36-41) — Déjà implémenté :**
```python
def get_orchestrator() -> LangGraphOrchestrator:
    """Dependency function to get the LangGraphOrchestrator instance."""
    return LangGraphOrchestrator()
```

✅ **Aucune modification nécessaire** — La dependency existe déjà.

### 3. `app/schemas/chat.py` (Optionnel)

**Emplacement :** `c:\genesis\app\schemas\chat.py`

**Potentielle extension :**
Ajouter des champs pour enrichir la réponse :
- `orchestration_confidence: float` — Confiance globale de l'orchestrateur
- `agents_status: Dict[str, str]` — Statut de chaque agent

---

## 🔄 Flow d'Exécution Cible

```
1. Utilisateur envoie message: "Je veux créer un site pour mon restaurant Chez Mama à Dakar"
                                    │
                                    ▼
2. chat_endpoint reçoit le message
   - Extrait: business_name="Chez Mama", sector="restaurant", location="Dakar"
                                    │
                                    ▼
3. Appel orchestrator.run({
     user_id: current_user.id,
     brief_id: uuid.uuid4(),
     business_brief: { business_name, sector, vision, mission, ... }
   })
                                    │
                                    ▼
4. LangGraph exécute les 5 agents en parallèle:
   ┌─────────────────────────────────────────────────────────┐
   │  research ──┬── content ──► END                         │
   │             ├── logo    ──► END                         │
   │             ├── seo     ──► END                         │
   │             └── template──► END                         │
   └─────────────────────────────────────────────────────────┘
                                    │
                                    ▼
5. Résultat orchestrator:
   {
     market_research: {...},
     content_generation: {...},
     logo_creation: {...},
     seo_optimization: {...},
     template_selection: {...},
     overall_confidence: 0.8,
     is_ready_for_website: true
   }
                                    │
                                    ▼
6. BriefToSiteTransformer.transform(brief) → SiteDefinition
                                    │
                                    ▼
7. Sauvegarde en Redis/DB + Retour ChatResponse
```

---

## ⚠️ Points d'Attention

### 1. Extraction du Business Context

Le message utilisateur est en langage naturel. Tu dois extraire les informations structurées :

**Option A — Regex simple (recommandé pour MVP) :**
```python
def extract_business_context(message: str) -> Dict[str, Any]:
    """Extraction basique pour Phase 2 MVP"""
    return {
        "business_name": "Entreprise",  # À extraire ou demander
        "industry_sector": "default",
        "vision": message[:200],
        "mission": message[:200],
        "location": {"country": "Sénégal", "city": "Dakar"},
        "services": [],
        "target_market": "",
        "competitive_advantage": ""
    }
```

**Option B — Utiliser un LLM pour extraction (Phase 2+) :**
Appeler un prompt d'extraction avant l'orchestration.

### 2. Gestion des Erreurs

L'orchestrateur a déjà des fallbacks gracieux. Assure-toi de :
- Logger les erreurs avec `structlog`
- Retourner une réponse utilisable même si certains agents échouent
- Vérifier `is_ready_for_website` avant de générer le site

### 3. Création du BusinessBrief en DB

Le `BriefToSiteTransformer` attend un objet `BusinessBrief` (modèle SQLAlchemy).

**Modèle existant :** `app/models/coaching.py`

```python
class BusinessBrief(Base):
    __tablename__ = "business_briefs"
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    business_name = Column(String)
    sector = Column(String)
    vision = Column(Text)
    mission = Column(Text)
    # ... autres champs
    
    # Résultats agents (JSON)
    market_research = Column(JSON)
    content_generation = Column(JSON)
    logo_creation = Column(JSON)
    seo_optimization = Column(JSON)
    template_selection = Column(JSON)
```

### 4. Clés API Requises

Les sub-agents utilisent des APIs externes :

| Agent | API | Variable |
|-------|-----|----------|
| ResearchSubAgent | Tavily/Kimi | `TAVILY_API_KEY` |
| ContentSubAgent | Deepseek | `DEEPSEEK_API_KEY` |
| LogoAgent | LogoAI | `LOGOAI_API_KEY` |
| SeoAgent | Tavily | `TAVILY_API_KEY` |

**Vérifier que ces clés sont dans le `.env` et chargées dans Docker.**

---

## ✅ Critères d'Acceptation

- [ ] Le endpoint `/api/v1/chat` appelle `LangGraphOrchestrator.run()` au lieu du mock
- [ ] Les 5 sub-agents s'exécutent (vérifier dans les logs)
- [ ] Le résultat est transformé en `SiteDefinition` valide
- [ ] Le site généré est sauvegardé en Redis/DB
- [ ] La réponse `ChatResponse` contient `site_data` avec le site complet
- [ ] Fallback gracieux si un agent échoue (au moins 3/5 requis)
- [ ] Tests unitaires pour la nouvelle logique
- [ ] Pas de régression sur les tests E2E existants

---

## 🧪 Tests

### Lancer les tests existants

```bash
# Dans le container genesis-api
docker exec -it genesis-api pytest tests/test_api/test_chat.py -v

# Ou depuis l'hôte avec docker-compose.test.yml
docker-compose -f docker-compose.test.yml up --abort-on-container-exit genesis-test-runner
```

### Test manuel via curl

```bash
# 1. Obtenir un token
$token = (Invoke-WebRequest -Uri "http://localhost:8002/api/v1/auth/token" `
  -Method POST `
  -Body "username=test@genesis.ai&password=test123456" `
  -ContentType "application/x-www-form-urlencoded" | 
  ConvertFrom-Json).access_token

# 2. Envoyer un message chat
Invoke-WebRequest -Uri "http://localhost:8002/api/v1/chat/" `
  -Method POST `
  -Headers @{"Authorization"="Bearer $token"} `
  -Body '{"message": "Je veux créer un site pour mon restaurant Chez Mama à Dakar"}' `
  -ContentType "application/json"
```

### Tests E2E (validation finale)

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit e2e-tests
```

**Résultat attendu :** 19/19 tests passés (comme Phase 1B)

---

## 📤 Livraison

1. **Commit convention :** `feat(chat): integrate LangGraph orchestrator for real AI generation`
2. **Push sur la branche :** `git push origin feature/GEN-13-langgraph-chat`
3. **Notifier le Tech Lead** pour review

---

## 📞 Support

En cas de blocage :
1. Consulter les logs : `docker logs genesis-api --tail 100`
2. Vérifier les clés API dans `.env`
3. Consulter `app/core/orchestration/langgraph_orchestrator.py` (299 lignes documentées)
4. Escalader au Tech Lead avec diagnostic détaillé

---

**Bonne implémentation !**

*Tech Lead Genesis AI*  
*18 décembre 2025*
