# 📋 Checklist Déploiement Genesis AI Staging

## ✅ **Phase 1 : Préparation (Terminée)**
- [x] Repository Git configuré et synchronisé
- [x] Configuration Docker Compose staging créée  
- [x] Script de déploiement automatisé créé
- [x] Fichiers poussés vers GitHub

## 🔄 **Phase 2 : Déploiement Serveur (En cours)**

### **Étape 2.1 : Connexion Serveur Staging**
```bash
# Connectez-vous à votre serveur staging où DigitalCloud360 est installé
ssh user@your-staging-server.com
```

### **Étape 2.2 : Vérification Prérequis Serveur**
```bash
# Vérifier Docker et Docker Compose
docker --version
docker-compose --version

# Vérifier que DigitalCloud360 fonctionne
docker ps | grep digitalcloud360
curl http://localhost:8000/health  # DigitalCloud360
```

### **Étape 2.3 : Préparation Variables d'Environnement**
**IMPORTANT :** Préparez ces clés API avant le déploiement :

```bash
# Variables obligatoires à configurer :
DIGITALCLOUD360_SERVICE_SECRET=xxxxx  # Secret pour communication service-to-service
GENESIS_AI_SECRET_KEY=xxxxx          # Clé secrète Genesis AI (générer une forte)
OPENAI_API_KEY=sk-xxxxx              # Clé OpenAI pour GPT-4o
TAVILY_API_KEY=tvly-xxxxx            # Clé Tavily pour recherche internet
LOGOAI_API_KEY=xxxxx                 # Clé LogoAI pour génération logos
```

### **Étape 2.4 : Exécution Déploiement**
```bash
# Télécharger et lancer le script de déploiement
wget https://raw.githubusercontent.com/digitalcigit/digitalcloud360_generis/master/deploy-staging.sh
chmod +x deploy-staging.sh
sudo ./deploy-staging.sh
```

**Le script va :**
1. Cloner le repository Genesis AI
2. Configurer l'environnement staging
3. Construire les images Docker
4. Démarrer les services (Genesis AI sur port 8001)
5. Exécuter les migrations DB
6. Vérifier la santé des services

---

## 🔍 **Phase 3 : Vérification Déploiement**

### **Étape 3.1 : Health Checks**
```bash
# Vérifier que Genesis AI répond
curl http://localhost:8001/health

# Vérifier les containers
sudo docker-compose -f /opt/genesis-ai/docker-compose.staging.yml ps

# Vérifier les logs
sudo docker-compose -f /opt/genesis-ai/docker-compose.staging.yml logs genesis-ai
```

### **Étape 3.2 : Test API Genesis AI**
```bash
# Test endpoint de base
curl http://localhost:8001/docs  # Documentation Swagger

# Test interconnexion avec DigitalCloud360
curl -X GET http://localhost:8001/api/v1/health/digitalcloud360
```

---

## 🧪 **Phase 4 : Tests UAT (User Acceptance Testing)**

### **Étape 4.1 : Tests Techniques Automatisés**
```bash
cd /opt/genesis-ai

# Lancer les tests depuis le container
sudo docker-compose -f docker-compose.staging.yml exec genesis-ai pytest tests/ -v

# Test spécifique authentication
sudo docker-compose -f docker-compose.staging.yml exec genesis-ai pytest tests/test_api/test_auth.py -v
```

### **Étape 4.2 : Tests Fonctionnels Manuels**

#### **Test 1 : Génération Business Brief**
```bash
curl -X POST http://localhost:8001/api/v1/business/brief/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TEST_TOKEN" \
  -d '{
    "session_id": "test_session_001",
    "business_name": "Mon Restaurant Africain",
    "sector": "restauration",
    "location": "Dakar, Sénégal",
    "description": "Restaurant traditionnel sénégalais"
  }'
```

#### **Test 2 : Récupération Brief**
```bash
curl -X GET http://localhost:8001/api/v1/business/brief/BRIEF_ID \
  -H "Authorization: Bearer YOUR_TEST_TOKEN"
```

#### **Test 3 : Création Site Web**
```bash
curl -X POST http://localhost:8001/api/v1/business/website/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TEST_TOKEN" \
  -d '{"brief_id": "BRIEF_ID"}'
```

### **Étape 4.3 : Tests Performance**
```bash
# Test charge avec Apache Bench (10 utilisateurs simultanés)
ab -n 100 -c 10 http://localhost:8001/health

# Test charge génération brief (simulation)
# À faire avec des vraies requêtes authentifiées
```

---

## 🔗 **Phase 5 : Validation Interconnexion DigitalCloud360**

### **Étape 5.1 : Test Communication Services**
```bash
# Depuis le container Genesis AI, tester la connexion vers DigitalCloud360
sudo docker-compose -f /opt/genesis-ai/docker-compose.staging.yml exec genesis-ai \
  curl http://digitalcloud360:8000/health

# Test réseau Docker
sudo docker network ls | grep digitalcloud360
```

### **Étape 5.2 : Test End-to-End Complet**
1. **Créer session coaching** via Genesis AI
2. **Générer business brief** complet (5 sub-agents)
3. **Appeler DigitalCloud360** pour création site
4. **Vérifier site créé** dans DigitalCloud360

---

## ⚠️ **Troubleshooting Commun**

### **Problème : Genesis AI ne démarre pas**
```bash
# Vérifier les logs détaillés
sudo docker-compose -f /opt/genesis-ai/docker-compose.staging.yml logs genesis-ai

# Vérifier la configuration
sudo docker-compose -f /opt/genesis-ai/docker-compose.staging.yml config
```

### **Problème : Erreur connexion DigitalCloud360**
```bash
# Vérifier le réseau Docker
sudo docker network inspect digitalcloud360_default

# Tester la connectivité
sudo docker-compose -f /opt/genesis-ai/docker-compose.staging.yml exec genesis-ai \
  ping digitalcloud360
```

### **Problème : Clés API manquantes**
```bash
# Éditer le fichier d'environnement
sudo nano /opt/genesis-ai/.env

# Redémarrer après modification
sudo docker-compose -f /opt/genesis-ai/docker-compose.staging.yml restart
```

---

## 📊 **Critères de Validation UAT**

### **✅ Critères Techniques**
- [ ] Genesis AI démarre en < 10 secondes
- [ ] Health check répond en < 1 seconde
- [ ] Tous les containers sont "healthy"
- [ ] Logs ne montrent aucune erreur critique

### **✅ Critères Fonctionnels**
- [ ] Génération business brief fonctionne (5 sub-agents)
- [ ] Sauvegarde/récupération Redis VFS opérationnelle
- [ ] Création site DigitalCloud360 réussie
- [ ] APIs authentification fonctionnelles

### **✅ Critères Performance**
- [ ] Response time API < 3 secondes
- [ ] Support 10 utilisateurs simultanés
- [ ] Génération brief complet < 30 secondes
- [ ] Pas de memory leaks après 1h utilisation

---

## 🎯 **Go/No-Go Production**

**✅ GO Production si :**
- Tous critères UAT validés
- Aucune erreur critique en logs
- Performance acceptable
- Interconnexion DigitalCloud360 stable

**❌ NO-GO si :**
- Erreurs durant génération brief
- Problèmes interconnexion services
- Performance inacceptable
- Instabilité après 24h fonctionnement

---

**Status Actuel :** 📋 Prêt pour déploiement serveur staging
