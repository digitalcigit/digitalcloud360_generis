# 🐳 WORK ORDER - Containerisation Genesis AI Deep Agents

**WO-001 | Date :** 19 août 2025  
**Assigné à :** TRAE  
**Priorité :** 🔴 **CRITIQUE** - Résout bloquant PostgreSQL actuel  
**Durée estimée :** 2-3 heures  
**Objectif :** Containeriser Genesis AI pour environnement de développement stable

---

## 🎯 **Contexte et Objectif**

### **Problème Actuel**
- ❌ Bloquant PostgreSQL (`OSError: [Errno 10061]`)
- ❌ Configuration environnement instable
- ❌ Développement à l'arrêt

### **Solution : Containerisation Complète**
- ✅ PostgreSQL + Redis dans containers
- ✅ Environnement reproductible et isolé
- ✅ Configuration standardisée
- ✅ Déblocage immédiat du développement

---

## 📋 **Tâches à Réaliser**

### **Phase 1 : Préparation (30 min)**

#### **Tâche 1.1 : Copier les fichiers Docker**
```bash
# Copier Dockerfile depuis spécifications
cp D:\genesis\docs\genesis-ai-technical-specification\Dockerfile D:\genesis\

# Copier docker-compose.yml
cp D:\genesis\docs\genesis-ai-technical-specification\docker-compose.yml D:\genesis\
```

#### **Tâche 1.2 : Vérifier Docker Desktop**
- [ ] S'assurer que Docker Desktop est installé et en cours d'exécution
- [ ] Vérifier version Docker : `docker --version`
- [ ] Tester : `docker run hello-world`

#### **Tâche 1.3 : Créer .dockerignore**
```bash
# Créer .dockerignore à la racine
echo "venv/
__pycache__/
*.pyc
.env
.git/
docs/
tests/
.pytest_cache/" > .dockerignore
```

### **Phase 2 : Configuration Environnement (45 min)**

#### **Tâche 2.1 : Vérifier ports disponibles**
```bash
# Vérifier ports libres sur la machine
netstat -an | findstr ":8000 :8001 :8002 :8003 :5432 :5433 :5434 :5435 :6379 :6380 :6381 :6382"  # Windows
# ou
netstat -tulpn | grep -E ":800[0-5]|:543[2-8]|:637[9]|:638[0-5]"  # Linux

# Ports OCCUPÉS identifiés: 8001, 5433, 5434, 6379, 6381
# Ports alternatifs LIBRES recommandés:
# - API Genesis: 8002, 8003, 8004, 8005
# - PostgreSQL: 5435, 5436, 5437, 5438  
# - Redis: 6382, 6383, 6384, 6385
```

#### **Tâche 2.2 : Adapter docker-compose.yml pour ports libres**
```yaml
# Configuration ports LIBRES pour éviter conflits :
services:
  genesis-api:
    ports:
      - "8002:8000"  # Port 8002 libre (8000, 8001 occupés)
  
  postgres:
    ports:
      - "5435:5432"  # Port 5435 libre (5432, 5433, 5434 occupés)
  
  redis:
    ports:
      - "6382:6379"  # Port 6382 libre (6379, 6381 occupés)
```

#### **Tâche 2.3 : Adapter .env selon ports choisis**
```env
# Modifier .env pour utiliser les services Docker
# IMPORTANT: Garder port interne (après :) dans l'URL
DATABASE_URL=postgresql+asyncpg://genesis_user:genesis_pass@postgres:5432/genesis_db
REDIS_URL=redis://redis:6379/0

# Variables application
APP_NAME="Genesis AI Deep Agents"
DEBUG=true
LOG_LEVEL=INFO
```

#### **Tâche 2.4 : Vérifier requirements.txt**
- [ ] S'assurer que toutes les dépendances sont présentes
- [ ] Vérifier présence de `asyncpg`, `redis`, `fastapi`, `uvicorn`

#### **Tâche 2.5 : Créer alembic/ si manquant**
```bash
# Si dossier alembic n'existe pas
mkdir alembic
touch alembic/__init__.py
```

### **Phase 3 : Build et Démarrage (30 min)**

#### **Tâche 3.1 : Build des images**
```bash
cd D:\genesis

# Build complet avec logs
docker-compose build --no-cache
```

#### **Tâche 3.2 : Démarrage des services**
```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier statut
docker-compose ps
```

#### **Tâche 3.3 : Validation démarrage**
```bash
# Vérifier logs application
docker-compose logs genesis-api

# Test endpoint health (port 8002 libre confirmé)
curl http://localhost:8002/health

# Test endpoint docs  
# Ouvrir http://localhost:8002/docs dans navigateur
```

### **Phase 4 : Tests et Validation (45 min)**

#### **Tâche 4.1 : Tests de connectivité**
- [ ] **PostgreSQL** : Vérifier connexion DB
- [ ] **Redis** : Tester cache/sessions
- [ ] **API** : Endpoints répondent correctement

#### **Tâche 4.2 : Exécuter suite de tests**
```bash
# Tests dans container
docker-compose exec genesis-api pytest tests/ -v

# Ou tests depuis host
docker-compose run --rm genesis-api pytest tests/ -v
```

#### **Tâche 4.3 : Tests endpoints API**
- [ ] GET `/health` → Status 200
- [ ] GET `/docs` → Interface Swagger accessible  
- [ ] POST `/api/v1/auth/validate` → 501 (placeholder normal)
- [ ] POST `/api/v1/coaching/start` → 501 (placeholder normal)

---

## ✅ **Critères de Validation**

### **Tests de Réussite**
- [ ] `docker-compose up` démarre sans erreur
- [ ] Application accessible sur port configuré (http://localhost:8002)
- [ ] Base PostgreSQL connectée et opérationnelle
- [ ] Redis fonctionnel pour cache
- [ ] Swagger UI accessible sur `/docs`
- [ ] Tests pytest passent (même si placeholders)

### **Performance Attendue**
- [ ] Démarrage complet < 2 minutes
- [ ] Réponse API < 500ms
- [ ] Aucune erreur dans logs containers

---

## 🚨 **Troubleshooting Rapide**

### **Problème : Build échoue**
```bash
# Nettoyer et rebuilder
docker-compose down -v
docker system prune -f
docker-compose build --no-cache
```

### **Problème : PostgreSQL ne démarre pas**
```bash
# Vérifier volumes et permissions
docker-compose logs postgres
docker volume ls | grep genesis
```

### **Problème : Application ne se connecte pas à la DB**
```bash
# Vérifier réseau Docker
docker-compose exec genesis-api ping postgres
docker-compose exec postgres pg_isready
```

---

## 📊 **Livrables Attendus**

### **À la fin de ce Work Order :**
1. ✅ Environnement Genesis AI complètement containerisé
2. ✅ Plus de bloquant PostgreSQL
3. ✅ Environnement de développement stable et reproductible
4. ✅ Base solide pour reprise développement fonctionnel
5. ✅ Documentation mise à jour avec commandes Docker

### **Prochaine étape :**
Reprise développement authentification JWT (`app/api/v1/auth.py`) dans environnement stable.

---

## 🎯 **Impact Business**

**Avant :** Développement bloqué, équipe en attente  
**Après :** Environnement stable, développement productif immédiat  
**ROI :** Déblocage projet + gain temps équipe + standardisation environnement

---

**💡 Note TRAE :** Cette containerisation résout ton bloquant PostgreSQL ET prépare l'environnement de production. Approche recommandée par l'architecture projet !

**🚀 Status Final Attendu : Genesis AI opérationnel en mode containerisé !**
