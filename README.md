# 🚀 Genesis AI Deep Agents Service

<div align="center">

![Genesis AI](https://img.shields.io/badge/Genesis%20AI-1.0.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-green?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)

**Premier Coach IA Personnel pour Entrepreneurs Africains avec Deep Agents LangGraph**

</div>

## 📖 Vue d'ensemble

Genesis AI est un service d'intelligence artificielle révolutionnaire conçu spécifiquement pour accompagner les entrepreneurs africains dans la création et le développement de leurs entreprises. Utilisant une architecture avancée de "Deep Agents" basée sur LangGraph, notre plateforme offre un coaching personnalisé et intelligent.

### 🎯 Mission

Démocratiser l'entrepreneuriat en Afrique en fournissant un coach IA accessible, intelligent et culturellement adapté aux défis spécifiques du continent africain.

## ✨ Fonctionnalités principales

### 🤖 **Deep Agents Intelligence**
- **Orchestration LangGraph** : Coordination intelligente de multiples agents spécialisés
- **Coaching personnalisé** : Accompagnement adapté au contexte entrepreneurial africain
- **Génération de business plans** : Création automatique de briefs business complets
- **Analyses de marché** : Études de faisabilité et recommandations stratégiques

### 🔌 **Intégrations avancées**
- **DigitalCloud360** : Orchestration d'agents IA professionnels
- **Tavily Search** : Recherche web intelligente et extraction de données
- **Redis Virtual FS** : Système de fichiers virtuel pour stockage temporaire
- **OpenAI & Anthropic** : Modèles d'IA de pointe
- **LogoAI** : Génération automatique de logos

### 🛡️ **Sécurité & Performance**
- **Authentification JWT** : Système d'authentification sécurisé
- **Health Checks** : Monitoring en temps réel des services
- **Logging structuré** : Traçabilité complète des opérations
- **Métriques Prometheus** : Monitoring et observabilité

## 🏗️ Architecture

```mermaid
graph TB
    A[Client Web/Mobile] --> B[FastAPI Gateway]
    B --> C[LangGraph Orchestrator]
    C --> D[Business Agent]
    C --> E[Research Agent]
    C --> F[Market Agent]
    
    B --> G[Authentication Service]
    B --> H[Redis Virtual FS]
    B --> I[PostgreSQL Database]
    
    C --> J[DigitalCloud360 API]
    C --> K[Tavily Search API]
    C --> L[OpenAI API]
    C --> M[Anthropic API]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style G fill:#fff3e0
```

## 🚀 Démarrage rapide

### Prérequis

- **Python 3.11+**
- **Docker & Docker Compose**
- **PostgreSQL 15+**
- **Redis 7+**

### Installation

1. **Cloner le repository**
```bash
git clone https://github.com/your-org/genesis-ai-service.git
cd genesis-ai-service
```

2. **Configuration de l'environnement**
```bash
# Copier le fichier d'environnement
cp .env.example .env

# Éditer les variables d'environnement
nano .env
```

3. **Variables d'environnement essentielles**
```bash
# Base de données
DATABASE_URL=postgresql+asyncpg://genesis_user:password@localhost:5435/genesis_db

# Services externes
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
TAVILY_API_KEY=your-tavily-key
DIGITALCLOUD360_SERVICE_SECRET=your-dc360-secret

# Redis
REDIS_URL=redis://redis:6379/0
```

### 🐋 Démarrage avec Docker (Recommandé)

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier l'état des services
docker-compose ps

# Voir les logs
docker-compose logs -f genesis-api
```

### 💻 Démarrage en développement local

```bash
# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Démarrer la base de données PostgreSQL
docker-compose up -d postgres redis

# Démarrer l'application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Documentation API

### Swagger UI
- **URL** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Endpoints principaux

#### 🔐 **Authentication**
```bash
# Inscription
POST /api/v1/auth/register

# Connexion
POST /api/v1/auth/token

# Profil utilisateur
GET /api/v1/auth/me
```

#### 🤖 **Coaching IA**
```bash
# Démarrer une session de coaching
POST /api/v1/coaching/start

# Progression dans les étapes
POST /api/v1/coaching/step
```

#### 💼 **Business Intelligence**
```bash
# Générer un brief business
POST /api/v1/business/brief/generate

# Récupérer un brief
GET /api/v1/business/brief/{brief_id}

# Résultats des sous-agents
GET /api/v1/business/brief/{brief_id}/results
```

#### 🔌 **Intégrations**
```bash
# Health check de tous les services
GET /api/v1/integrations/health

# Recherche web avec Tavily
POST /api/v1/integrations/tavily/search

# Gestion fichiers Redis FS
POST /api/v1/integrations/redis-fs/write
GET /api/v1/integrations/redis-fs/read

# Agents DigitalCloud360
GET /api/v1/integrations/digitalcloud360/agents
POST /api/v1/integrations/digitalcloud360/agents
```

## 🧪 Tests

### Tests unitaires

```bash
# Tous les tests
pytest

# Tests avec coverage
pytest --cov=app --cov-report=html

# Tests spécifiques
pytest tests/test_api/test_auth.py -v
pytest tests/test_integrations/ -v
```

### Tests Docker

```bash
# Script PowerShell (Windows)
.\scripts\test-docker.ps1 all

# Tests d'authentification uniquement
.\scripts\test-docker.ps1 auth

# Tests d'intégrations uniquement  
.\scripts\test-docker.ps1 integrations
```

### Tests multi-environnements

```bash
# Validation du système de profils
.\test_profiles.sh

# Tests environnement local
TEST_PROFILE=local pytest tests/

# Tests environnement Docker
TEST_PROFILE=docker pytest tests/
```

## 🔧 Configuration avancée

### Profils d'environnement

| Profil | Base de données | Redis | Usage |
|--------|-----------------|-------|-------|
| **local** | PostgreSQL localhost:5433 | localhost:6379 | Développement local |
| **docker** | PostgreSQL test-db:5432 | redis:6379 | Tests conteneurisés |
| **production** | PostgreSQL externe | Redis externe | Production |

### Configuration de testing

```python
# Configuration automatique selon l'environnement
from tests.conftest_profile import *

# Les fixtures sont automatiquement sélectionnées :
# - conftest_local.py pour environnement local
# - conftest_docker.py pour environnement Docker
```

## 🔍 Monitoring & Observabilité

### Health Checks

```bash
# Santé générale
GET /health

# Santé détaillée
GET /health/detailed

# Santé des intégrations
GET /health/integrations
```

### Métriques Prometheus

```bash
# Métriques applicatives
GET /metrics

# Port Prometheus
http://localhost:8001/metrics
```

### Logs structurés

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "service": "genesis-ai",
  "operation": "coaching_session_start",
  "user_id": "user-123",
  "session_id": "session-456",
  "duration_ms": 150
}
```

## 🔌 Guide des intégrations

### Tavily Search

```python
from app.integrations.tavily import TavilyClient

client = TavilyClient()

# Recherche intelligente
results = await client.search(
    "startup fintech Afrique",
    search_depth="deep",
    max_results=10
)

# Extraction de contenu
content = await client.extract_content("https://example.com")
```

### Redis Virtual File System

```python
from app.integrations.redis_fs import RedisVirtualFileSystem

fs = RedisVirtualFileSystem()

# Écriture de fichier
await fs.write_file("/session/user123/data.json", content, ttl=3600)

# Lecture de fichier
content = await fs.read_file("/session/user123/data.json")

# Liste des fichiers
files = await fs.list_files("/session/user123/")
```

### DigitalCloud360

```python
from app.integrations.digitalcloud360 import DigitalCloud360APIClient

client = DigitalCloud360APIClient()

# Lister les agents
agents = await client.list_agents()

# Créer un agent
agent = await client.create_agent({
    "name": "Business Advisor",
    "capabilities": ["consulting", "analysis"]
})
```

## 🛠️ Développement

### Structure du projet

```
genesis-ai-service/
├── app/                          # Code source principal
│   ├── api/                      # Endpoints API
│   │   └── v1/                   # Version 1 de l'API
│   ├── core/                     # Logique métier centrale
│   │   ├── integrations/         # Clients d'intégration
│   │   ├── orchestration/        # LangGraph orchestrateurs
│   │   └── security/             # Authentification & sécurité
│   ├── models/                   # Modèles SQLAlchemy
│   ├── schemas/                  # Schémas Pydantic
│   ├── services/                 # Services métier
│   └── config/                   # Configuration
├── tests/                        # Tests automatisés
│   ├── test_api/                 # Tests endpoints API
│   ├── test_integrations/        # Tests intégrations
│   └── conftest*.py              # Configuration tests
├── docs/                         # Documentation
├── scripts/                      # Scripts utilitaires
└── docker-compose*.yml          # Configuration Docker
```

### Contribuer

1. **Fork** le repository
2. **Créer** une branche feature (`git checkout -b feature/amazing-feature`)
3. **Commit** les changements (`git commit -m 'Add amazing feature'`)
4. **Push** vers la branche (`git push origin feature/amazing-feature`)
5. **Ouvrir** une Pull Request

### Standards de code

- **PEP 8** : Style de code Python
- **Type hints** : Annotations de types obligatoires
- **Docstrings** : Documentation des fonctions
- **Tests** : Coverage minimum 80%

## 🚀 Déploiement

### Production avec Docker

```bash
# Build image de production
docker build -t genesis-ai:latest .

# Démarrage production
docker-compose -f docker-compose.prod.yml up -d

# Mise à jour
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### Variables d'environnement production

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/genesis
REDIS_URL=redis://prod-redis:6379/0
SENTRY_DSN=your-sentry-dsn
```

## 📊 Métriques & KPI

### Métriques techniques
- **Latence** : < 200ms pour 95% des requêtes
- **Availability** : > 99.9% uptime
- **Throughput** : 1000+ requêtes/seconde
- **Error rate** : < 0.1%

### Métriques métier
- **Sessions de coaching** : Nombre de sessions actives
- **Business briefs** : Plans d'affaires générés
- **Taux de conversion** : Utilisateurs actifs vs inscrits
- **Satisfaction** : Score de satisfaction utilisateur

## 🤝 Support & Communauté

- **Documentation** : [docs.genesis-ai.com](https://docs.genesis-ai.com)
- **Support** : support@genesis-ai.com
- **Issues** : [GitHub Issues](https://github.com/your-org/genesis-ai-service/issues)
- **Discord** : [Communauté Genesis AI](https://discord.gg/genesis-ai)

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **Équipe Genesis AI** : Développement et vision produit
- **Communauté open source** : FastAPI, LangGraph, SQLAlchemy
- **Entrepreneurs africains** : Inspiration et retours utilisateurs

---

<div align="center">

**Genesis AI - Transforming African Entrepreneurship with AI**

![Made with ❤️ in Africa](https://img.shields.io/badge/Made%20with%20❤️%20in-Africa-green?style=for-the-badge)

</div>