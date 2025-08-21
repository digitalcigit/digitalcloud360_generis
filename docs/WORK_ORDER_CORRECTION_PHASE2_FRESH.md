# WORK ORDER - CORRECTION & FINALISATION PHASE 2
## Session Fraîche TRAE - Rectification Perception vs Réalité

**Date :** Nouvelle session
**Assigné à :** TRAE (IA Senior Dev)
**Priorité :** CRITIQUE - Correction immédiate perception erronée
**Deadline :** 24-48h maximum

---

## **CONTEXT CRITIQUE : RECTIFICATION MAJEURE**

### **❌ PERCEPTION ERRONÉE TRAE (Rapport Mi-Parcours)**
- **"Sub-Agents : Non commencé"** 
- **"Orchestrateur : Non démarré"**
- **"Intégrations : Non commencées"**
- **"Business API : Placeholders seulement"**

### **✅ RÉALITÉ CODE BASE (Vérification Factuelle)**
- **Sub-Agents :** 5 agents ENTIÈREMENT implémentés dans `app/core/agents/`
- **Orchestrateur :** LangGraph COMPLET dans `app/core/orchestration/`
- **Intégrations :** 5 clients API FONCTIONNELS dans `app/core/integrations/`
- **Business API :** Logique métier ACTIVE avec orchestration réelle

---

## **TÂCHES CRITIQUES IMMÉDIATES**

### **1. RECTIFICATION PERCEPTION (URGENT)**
**Temps estimé :** 30 minutes

- [ ] **Examiner RÉELLEMENT le code dans :**
  - `app/core/agents/` (5 agents complets)
  - `app/core/orchestration/langgraph_orchestrator.py`
  - `app/core/integrations/` (5 clients API)
  - `app/api/v1/business.py` (logique active)

- [ ] **Reconnaître l'état d'avancement réel :** ~85% Phase 2 déjà implémentée

### **2. CORRECTION TESTS ENVIRONMENT (PRIORITÉ 1)**
**Temps estimé :** 2-3 heures

#### **2.1 Fixes Imports Tests - URGENT**
```python
# Dans tests/test_api/test_coaching.py (ligne ~4)
import json  # ← MANQUANT - Ajouter

# Autres imports manquants à identifier et corriger
```

#### **2.2 Fixes Authentication Tests - CRITIQUE**
- [ ] **URGENT:** Corriger erreurs 401 vs 200 dans `test_business.py`
- [ ] **URGENT:** Vérifier configuration auth mocks dans `conftest.py` 
- [ ] **URGENT:** Assurer token validation cohérente
- [ ] **URGENT:** Fixer `NameError: name 'json' is not defined` dans coaching tests

#### **2.3 Stabilisation Environment Test - BLOQUANT**
- [ ] **CRITIQUE:** Exécuter `pytest -v tests/` pour audit complet
- [ ] **CRITIQUE:** Corriger tous les fails identifiés un par un
- [ ] **CRITIQUE:** Atteindre 100% pass rate sur test suite
- [ ] **IMPORTANTE:** Documenter tous les fixes appliqués

#### **2.4 Tâches Techniques Spécifiques Identifiées**
- [ ] **Import json manquant** - tests/test_api/test_coaching.py ligne 4
- [ ] **AssertionError 401 != 200** - tests/test_api/test_business.py 
- [ ] **Auth headers configuration** - Vérifier conftest.py mocks
- [ ] **Exception classes enrichment** - app/utils/exceptions.py trop basique
- [ ] **CRITIQUE - Incohérence Docker/Tests** - Tests locaux vs app containerisée

#### **2.5 NOUVEAU: Alignement Architecture Docker-Tests (BLOQUANT)**
**Temps estimé :** 1-2 heures
- [ ] **URGENT:** Créer service `genesis-test` dans docker-compose.yml
- [ ] **URGENT:** Configuration test profile Docker pour isolation
- [ ] **URGENT:** Migration commandes pytest vers `docker-compose --profile test`
- [ ] **CRITIQUE:** Tests DATABASE_URL vers test-db container (ligne 86)

### **3. AMÉLIORATION EXCEPTIONS (PRIORITÉ 2)**
**Temps estimé :** 1 heure

#### **Actuel (`app/utils/exceptions.py`) :**
```python
class GenesisAIException(Exception):
    pass  # ← Trop simpliste
```

#### **À implémenter :**
```python
class GenesisAIException(Exception):
    def __init__(self, error_code: str, message: str, details: str = None):
        self.error_code = error_code
        self.message = message
        self.details = details
        super().__init__(self.message)
```

### **4. VALIDATION COMPLÈTE INTÉGRATION (PRIORITÉ 3)**
**Temps estimé :** 2 heures

- [ ] **Test orchestration end-to-end :**
  - Démarrer avec business brief sample
  - Vérifier exécution 5 agents en parallèle
  - Valider retour état final structuré

- [ ] **Test intégrations externes :**
  - Redis Virtual File System persistence
  - Clients API (mock ou sandbox si clés disponibles)
  - Gestion erreurs et timeouts

---

## **DELIVERABLES ATTENDUS**

### **Rapport Correction (Dans 4h)**
1. **Reconnaissance erreur perception**
2. **Liste fixes tests appliqués** 
3. **Résultats pytest 100% pass**
4. **Confirmation orchestration fonctionnelle**

### **Code Final Stabilisé (Dans 24h)**
- Tests environment 100% stable
- Exceptions classes enrichies
- Documentation mise à jour
- Démo orchestration end-to-end

---

## **MÉTHODOLOGIE STRICTE**

### **Étape 1 : AUDIT RÉEL (30 min)**
```bash
# Examiner VRAIMENT le code
find app/core -name "*.py" -exec wc -l {} +
grep -r "class.*Agent" app/core/agents/
grep -r "LangGraphOrchestrator" app/core/orchestration/
```

### **Étape 2 : TESTS FIXES (2h)**
```bash
# Exécuter tests et corriger 1 par 1
pytest tests/ -v --tb=short
# Identifier fails spécifiques
# Appliquer fixes ciblés
# Re-test jusqu'à 100% pass
```

### **Étape 3 : VALIDATION INTÉGRATION (2h)**
```bash
# Test orchestration locale
python -c "
from app.core.orchestration.langgraph_orchestrator import LangGraphOrchestrator
orch = LangGraphOrchestrator()
print('Orchestrator initialized successfully')
"
```

---

## **CHECKLIST VALIDATION FINALE**

- [ ] **Perception corrigée :** Reconnaissance ~85% Phase 2 déjà fait
- [ ] **Tests environment stable :** pytest 100% pass
- [ ] **Exceptions enrichies :** Codes erreurs structurés
- [ ] **Orchestration validée :** End-to-end fonctionnel
- [ ] **Documentation à jour :** Reflect real state
- [ ] **Rapport correction produit :** Avec preuves factuelles

---

## **IMPORTANT : CHANGEMENT MINDSET**

### **❌ Ancien Mindset TRAE :**
*"Tout est à faire, rien n'est commencé, environnement bloquant"*

### **✅ Nouveau Mindset Requis :**
*"85% déjà implémenté, juste polishing et stabilisation tests needed"*

---

## **SUPPORT & RESSOURCES**

- **Code Base :** Déjà ~85% complet Phase 2
- **Documentation :** `docs/genesis-ai-technical-specification/`
- **Templates :** Fournis dans spécifications techniques
- **Environment :** Docker stable, juste tests à fixer

---

**DEADLINE FERME :** 24h pour correction complète + validation

**Contact :** IA Senior Dev Team Lead pour questions urgentes
