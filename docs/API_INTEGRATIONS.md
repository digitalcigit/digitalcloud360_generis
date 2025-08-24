# 🔌 Documentation API Intégrations - Genesis AI

## 📋 Vue d'ensemble

Genesis AI intègre plusieurs services externes pour offrir une expérience complète d'intelligence artificielle. Cette documentation présente les intégrations disponibles, leur configuration et leur utilisation.

## 🚀 Services Intégrés

### 1. **DigitalCloud360 API Client**
- **Fichier :** `app/integrations/digitalcloud360.py`
- **Purpose :** Intégration avec la plateforme DigitalCloud360 pour l'orchestration d'agents
- **Type :** Service d'orchestration d'agents IA

### 2. **Tavily Search Client**
- **Fichier :** `app/integrations/tavily.py`
- **Purpose :** Recherche web intelligente et extraction de données
- **Type :** Service de recherche web

### 3. **Redis Virtual File System**
- **Fichier :** `app/integrations/redis_fs.py`
- **Purpose :** Système de fichiers virtuel basé sur Redis
- **Type :** Stockage temporaire et cache

---

## 🔧 Configuration

### Variables d'environnement requises

```bash
# DigitalCloud360
DIGITALCLOUD360_API_URL=https://api.digitalcloud360.com
DIGITALCLOUD360_SERVICE_SECRET=your-service-secret
DIGITALCLOUD360_TIMEOUT=30

# Tavily
TAVILY_API_KEY=tvly-your-api-key
TAVILY_BASE_URL=https://api.tavily.com

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_GENESIS_AI_DB=0
REDIS_SESSION_TTL=7200
```

### Configuration de développement (`.env.test`)

```bash
# Clés de développement pour tests
DIGITALCLOUD360_SERVICE_SECRET=test-service-secret-genesis-ai
TAVILY_API_KEY=tvly-test-tavily-development-key
REDIS_URL=redis://localhost:6379/0
```

---

## 📚 Documentation des APIs

### 1. DigitalCloud360 API Client

#### **Initialisation**
```python
from app.integrations.digitalcloud360 import DigitalCloud360APIClient

client = DigitalCloud360APIClient()
```

#### **Méthodes disponibles**

##### `health_check() -> bool`
Vérifie l'état de santé du service DigitalCloud360.

```python
is_healthy = await client.health_check()
# Returns: True if service is available, False otherwise
```

##### `list_agents() -> List[Dict[str, Any]]`
Liste tous les agents disponibles sur la plateforme.

```python
agents = await client.list_agents()
# Returns: [{"id": "agent-1", "name": "Agent Assistant", "status": "active"}]
```

##### `create_agent(agent_data: Dict[str, Any]) -> Dict[str, Any]`
Crée un nouvel agent sur la plateforme.

```python
agent_data = {
    "name": "Business Advisor",
    "description": "Agent spécialisé en conseil d'affaires",
    "capabilities": ["consulting", "analysis"]
}
agent = await client.create_agent(agent_data)
# Returns: {"id": "new-agent-id", "name": "Business Advisor", ...}
```

##### `get_agent(agent_id: str) -> Dict[str, Any]`
Récupère les détails d'un agent spécifique.

```python
agent = await client.get_agent("agent-123")
# Returns: {"id": "agent-123", "name": "Agent Name", "status": "active"}
```

##### `update_agent(agent_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]`
Met à jour un agent existant.

```python
update_data = {"status": "inactive"}
agent = await client.update_agent("agent-123", update_data)
# Returns: Updated agent data
```

#### **Gestion des erreurs**

```python
from app.integrations.digitalcloud360 import DigitalCloud360APIError

try:
    agents = await client.list_agents()
except DigitalCloud360APIError as e:
    print(f"Erreur API: {e}")
except Exception as e:
    print(f"Erreur inattendue: {e}")
```

---

### 2. Tavily Search Client

#### **Initialisation**
```python
from app.integrations.tavily import TavilyClient

client = TavilyClient()
```

#### **Méthodes disponibles**

##### `health_check() -> bool`
Vérifie l'état de santé du service Tavily.

```python
is_healthy = await client.health_check()
# Returns: True if service is available, False otherwise
```

##### `search(query: str, **kwargs) -> Dict[str, Any]`
Effectue une recherche web intelligente.

```python
results = await client.search("intelligence artificielle startup")
# Returns: {
#     "query": "intelligence artificielle startup",
#     "results": [
#         {
#             "title": "Top AI Startups 2024",
#             "url": "https://example.com",
#             "content": "Description du contenu...",
#             "score": 0.95
#         }
#     ],
#     "answer": "Résumé des résultats de recherche"
# }
```

**Paramètres optionnels :**
```python
results = await client.search(
    query="IA startup",
    search_depth="deep",      # "basic" ou "deep"
    max_results=10,           # Nombre max de résultats
    include_domains=["techcrunch.com", "wired.com"],
    exclude_domains=["spam.com"]
)
```

##### `extract_content(url: str) -> Dict[str, Any]`
Extrait le contenu principal d'une URL.

```python
content = await client.extract_content("https://example.com/article")
# Returns: {
#     "url": "https://example.com/article",
#     "title": "Titre de l'article",
#     "content": "Contenu extrait...",
#     "author": "Nom de l'auteur",
#     "published_date": "2024-01-15"
# }
```

##### `get_search_context(query: str) -> str`
Obtient un contexte enrichi pour une requête.

```python
context = await client.get_search_context("startup fintech France")
# Returns: "Texte de contexte enrichi basé sur les résultats de recherche"
```

#### **Modes de fonctionnement**

##### Mode Mock (Développement)
```python
# Configuration automatique en mode TESTING_MODE=true
client = TavilyClient()  # Utilise automatiquement les données mock
```

##### Mode API Réelle (Production)
```python
# Nécessite TAVILY_API_KEY valide
client = TavilyClient()
results = await client.search("requête réelle")
```

---

### 3. Redis Virtual File System

#### **Initialisation**
```python
from app.integrations.redis_fs import RedisVirtualFileSystem

fs = RedisVirtualFileSystem()
```

#### **Méthodes disponibles**

##### `health_check() -> bool`
Vérifie l'état de santé de Redis.

```python
is_healthy = await fs.health_check()
# Returns: True if Redis is available, False otherwise
```

##### `write_file(path: str, content: str, ttl: Optional[int] = None) -> bool`
Écrit un fichier dans le système virtuel.

```python
success = await fs.write_file(
    "/session/user123/context.json",
    '{"step": "vision", "progress": 25}',
    ttl=3600  # Expire dans 1 heure
)
# Returns: True if successful, False otherwise
```

##### `read_file(path: str) -> Optional[str]`
Lit un fichier depuis le système virtuel.

```python
content = await fs.read_file("/session/user123/context.json")
# Returns: '{"step": "vision", "progress": 25}' or None if not found
```

##### `delete_file(path: str) -> bool`
Supprime un fichier du système virtuel.

```python
success = await fs.delete_file("/session/user123/context.json")
# Returns: True if deleted, False if not found
```

##### `file_exists(path: str) -> bool`
Vérifie l'existence d'un fichier.

```python
exists = await fs.file_exists("/session/user123/context.json")
# Returns: True if file exists, False otherwise
```

##### `list_files(prefix: str = "") -> List[str]`
Liste les fichiers avec un préfixe donné.

```python
files = await fs.list_files("/session/user123/")
# Returns: ["/session/user123/context.json", "/session/user123/history.txt"]
```

##### `get_file_info(path: str) -> Optional[Dict[str, Any]]`
Obtient les métadonnées d'un fichier.

```python
info = await fs.get_file_info("/session/user123/context.json")
# Returns: {
#     "path": "/session/user123/context.json",
#     "size": 256,
#     "created_at": "2024-01-15T10:30:00Z",
#     "ttl": 3600
# }
```

---

## 🧪 Tests et Validation

### Coverage des tests

Tous les clients d'intégration sont couverts par des tests unitaires complets :

- **DigitalCloud360** : 5 tests essentiels (100% coverage)
- **Tavily** : 10 tests complets (95% coverage)
- **Redis FS** : 14 tests approfondis (97% coverage)

### Exécution des tests

```bash
# Tests d'intégration spécifiques
pytest tests/test_integrations/ -v

# Tests par service
pytest tests/test_integrations/test_digitalcloud360.py -v
pytest tests/test_integrations/test_tavily.py -v
pytest tests/test_integrations/test_redis_fs.py -v

# Tests avec coverage
pytest tests/test_integrations/ --cov=app.integrations --cov-report=html
```

### Tests Docker

```bash
# Via script PowerShell
.\scripts\test-docker.ps1 integrations

# Via docker-compose
docker-compose -f docker-compose.test.yml run --rm genesis-test-integrations
```

---

## 🛡️ Health Checks

Tous les services intégrés supportent les health checks pour le monitoring :

```python
from app.core.health import check_all_integrations

# Vérification globale
health_status = await check_all_integrations()
# Returns: {
#     "redis": {"status": "healthy", "response_time": 0.02},
#     "digitalcloud360": {"status": "healthy", "response_time": 0.15},
#     "tavily": {"status": "healthy", "response_time": 0.08}
# }
```

### Endpoint Health Check

```bash
# Via API REST
curl http://localhost:8000/health

# Réponse type
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "services": {
        "database": "healthy",
        "redis": "healthy",
        "digitalcloud360": "healthy",
        "tavily": "healthy"
    }
}
```

---

## 🔒 Sécurité

### Authentification

- **DigitalCloud360** : Service secret configuré via `DIGITALCLOUD360_SERVICE_SECRET`
- **Tavily** : Clé API configurée via `TAVILY_API_KEY`
- **Redis** : Connexion sécurisée via URL avec authentification

### Bonnes pratiques

1. **Variables d'environnement** : Toujours utiliser des variables d'environnement pour les secrets
2. **Timeouts** : Tous les clients ont des timeouts configurés
3. **Rate limiting** : Respect des limites des APIs externes
4. **Retry logic** : Gestion des erreurs temporaires avec retry automatique

---

## 🐛 Troubleshooting

### Problèmes courants

#### DigitalCloud360 Connection Error
```python
# Vérifier la configuration
import os
print(os.getenv("DIGITALCLOUD360_API_URL"))
print(os.getenv("DIGITALCLOUD360_SERVICE_SECRET"))

# Tester la connectivité
client = DigitalCloud360APIClient()
health = await client.health_check()
print(f"Service healthy: {health}")
```

#### Tavily API Rate Limit
```python
# Erreur : TavilyAPIError with status 429
# Solution : Attendre et retry ou utiliser mode mock

client = TavilyClient()
# Le client gère automatiquement les retries
```

#### Redis Connection Issues
```python
# Vérifier Redis
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
try:
    redis_client.ping()
    print("✅ Redis connected")
except Exception as e:
    print(f"❌ Redis error: {e}")
```

---

## 📈 Métriques et Monitoring

### Métriques collectées

- **Temps de réponse** : Pour chaque appel API
- **Taux d'erreur** : Pourcentage d'échecs par service
- **Utilisation** : Nombre d'appels par service/heure
- **Disponibilité** : Uptime des services externes

### Logs structurés

```python
# Exemple de log automatique
{
    "timestamp": "2024-01-15T10:30:00Z",
    "service": "tavily",
    "operation": "search",
    "duration_ms": 150,
    "status": "success",
    "query": "startup fintech"
}
```

---

## 🔮 Roadmap

### Prochaines intégrations

1. **OpenAI GPT-4** : Intégration directe pour génération de contenu
2. **Anthropic Claude** : Client pour analyses complexes
3. **LogoAI** : Génération automatique de logos
4. **Elasticsearch** : Recherche avancée dans les données

### Améliorations prévues

- Cache intelligent pour Tavily
- Pool de connexions pour Redis
- Retry exponential backoff
- Circuit breaker pattern

---

**Documentation générée le 22 août 2025**  
**Version Genesis AI :** 1.0.0  
**Auteur :** Équipe Dev Genesis AI  
**Dernière mise à jour :** T5.2 Work Order Resolution