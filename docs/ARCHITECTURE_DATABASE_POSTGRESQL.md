# 🗄️ Architecture Base de Données PostgreSQL - Genesis AI

**Date :** 22 août 2025  
**Version :** 1.0  
**Suite à :** Work Order T4.1 - Harmonisation Configuration Database

---

## 🎯 **Vision Architecture**

**Décision :** **Option A - PostgreSQL partout** ✅  
Harmonisation complète sur PostgreSQL pour tous les environnements (dev/test/prod)

**Avantages :**
- ✅ Parité fonctionnelle complète entre environnements
- ✅ Tests plus fiables (même moteur de DB)
- ✅ Réduction de la complexité de configuration
- ✅ Préparation optimale pour la production

---

## 🏗️ **Architecture par Environnement**

### **🧪 Tests (TEST)**
```yaml
Service: test-db (Docker)
Port: 5433
Base: test_db
User: test_user
Pass: test_password
URL: postgresql+asyncpg://test_user:test_password@localhost:5433/test_db
```

**Usage :**
- Tests unitaires et d'intégration
- Tests depuis l'hôte (localhost:5433)
- Tests depuis conteneur (test-db:5432)

### **💻 Développement (DEV)**
```yaml
Service: postgres (Docker)
Port: 5435
Base: genesis_db
User: genesis_user
Pass: your_secure_password_here
URL: postgresql+asyncpg://genesis_user:password@localhost:5435/genesis_db
```

**Usage :**
- Développement local
- Débogage et tests manuels
- Prototypage de nouvelles fonctionnalités

### **🚀 Production (PROD)**
```yaml
Service: PostgreSQL managé (cloud)
Port: 5432
Base: genesis_ai_prod
User: genesis_prod_user
Pass: ${POSTGRES_PASSWORD}
URL: ${DATABASE_URL}
```

**Usage :**
- Production réelle
- Variables d'environnement sécurisées
- Connexions chiffrées et monitoring

---

## 📋 **Configuration Files**

### **Tests - `.env.test`**
```bash
TEST_DATABASE_URL=postgresql+asyncpg://test_user:test_password@localhost:5433/test_db
TESTING_MODE=true
STRICT_HEALTH_CHECKS=false
```

### **Développement - `.env.local`**
```bash
DATABASE_URL=postgresql+asyncpg://genesis_user:password@localhost:5435/genesis_db
ENVIRONMENT=development
DEBUG=true
```

### **Production - `.env.production`**
```bash
DATABASE_URL=${DATABASE_URL}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENVIRONMENT=production
STRICT_HEALTH_CHECKS=true
```

---

## 🐋 **Services Docker**

### **Test Database**
```yaml
test-db:
  image: postgres:15-alpine
  ports: ["5433:5432"]
  environment:
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_password
    POSTGRES_DB: test_db
```

### **Development Database**
```yaml
postgres:
  image: postgres:15-alpine
  ports: ["5435:5432"]
  environment:
    POSTGRES_USER: genesis_user
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: genesis_db
```

---

## 🔧 **Configuration App (`settings.py`)**

### **Database URL Assembly**
```python
@field_validator("DATABASE_URL", mode='before')
def assemble_db_connection(cls, v: Optional[str], values) -> str:
    """PostgreSQL uniquement - plus de SQLite"""
    if isinstance(v, str) and v:
        return v
    # Construction automatique PostgreSQL
    return f"postgresql+asyncpg://{user}:{password}@{server}:{port}/{db}"

@field_validator("TEST_DATABASE_URL", mode='before') 
def assemble_test_db_connection(cls, v: Optional[str], values) -> str:
    """PostgreSQL test uniquement"""
    if isinstance(v, str) and v:
        return v
    return "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"
```

### **Runtime Detection**
```python
# Détection automatique environnement conteneur vs hôte
if os.getenv("RUNNING_IN_DOCKER"):
    TEST_DB_HOST = "test-db:5432"
else:
    TEST_DB_HOST = "localhost:5433"
```

---

## 🧪 **Tests & Validation**

### **Tests Locaux**
```bash
# Démarrer services
docker-compose up -d test-db redis

# Tests authentification
pytest tests/test_api/test_auth.py -v

# Tests intégrations
pytest tests/test_integrations/ -v
```

### **Tests Conteneur**
```bash
# Depuis conteneur genesis-api
docker-compose exec genesis-api pytest tests/test_api/test_auth.py -v
```

### **Validation Cross-Platform**
```bash
# Local (PostgreSQL localhost:5433)
pytest tests/test_api/test_auth.py -v  # ✅ 6/6 passent

# Docker (PostgreSQL test-db:5432)  
docker-compose exec genesis-api pytest tests/test_api/test_auth.py -v  # ✅ 6/6 passent
```

---

## 📊 **Avantages de l'Architecture**

### **✅ Parité Environnementale**
- Même moteur PostgreSQL partout
- Comportement SQL identique
- Performance tests réalistes

### **✅ Simplicité Configuration**
- Un seul système de DB à maintenir
- Validation et déploiement simplifiés
- Documentation unifiée

### **✅ Fiabilité Tests**
- Tests plus représentatifs de la production
- Détection précoce des problèmes SQL
- Intégration continue robuste

### **✅ Scalabilité**
- PostgreSQL adapté aux gros volumes
- Extensions riches (JSON, recherche full-text)
- Optimisations avancées disponibles

---

## 🚨 **Migration depuis SQLite**

### **Fichiers Modifiés**
- ✅ `app/config/settings.py` - Validators PostgreSQL
- ✅ `tests/conftest.py` - URL PostgreSQL
- ✅ `.env.test` - Configuration PostgreSQL  
- ✅ `docker-compose.yml` - Exposition ports
- ✅ `.env.local` - Développement PostgreSQL
- ✅ `.env.production` - Production PostgreSQL

### **Validation Migration**
- ✅ Tests auth : 6/6 passent (local + Docker)
- ✅ Tests intégrations : 27/28 passent
- ✅ Application startup : OK
- ✅ Health checks : OK

---

## 🔄 **Commandes Utiles**

### **Gestion Services**
```bash
# Démarrer base test
docker-compose up -d test-db

# Démarrer base dev
docker-compose up -d postgres

# Status services
docker-compose ps

# Logs base de données
docker-compose logs test-db
```

### **Connexion Directe**
```bash
# Test DB
docker-compose exec test-db psql -U test_user -d test_db

# Dev DB  
docker-compose exec postgres psql -U genesis_user -d genesis_db
```

### **Backup/Restore**
```bash
# Backup test
docker-compose exec test-db pg_dump -U test_user test_db > backup_test.sql

# Restore test
docker-compose exec -T test-db psql -U test_user test_db < backup_test.sql
```

---

**Architecture validée le 22 août 2025**  
**Statut :** 🎯 Production Ready