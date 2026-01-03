# 📋 BRIEFING DEV SENIOR - Phase 2 Finalisation

**Date :** 25/12/2025 10:30 UTC  
**De :** Tech Lead Genesis AI  
**À :** Dev Senior  
**Priorité :** 🔴 CRITIQUE  

---

## 🎯 Mission Résumée

**Phase 2 est à 85% complète**, pas à 0% comme indiqué dans les docs.

**Travail restant :** Finalisation et stabilisation (8-11 jours)

---

## ✅ Ce Qui Existe Déjà (NE PAS TOUCHER)

1. **LogoAgent** - DALL-E 3 complet (236 lignes)
2. **LangGraphOrchestrator** - 5 agents intégrés (308 lignes)
3. **SiteRenderer Frontend** - Complet avec tests
4. **API Business** - POST /brief/generate, GET /brief/{id}
5. **API Sites** - GET /{site_id}/preview (existe dans sites.py)

---

## 🔧 Ce Qu'il Faut Corriger (4 Tâches Prioritaires)

### 1️⃣ SeoAgent - Remplacer Tavily par Kimi Search (2-3h)

**Fichier :** `app/core/agents/seo.py`

**Problème :** Utilise `TavilyClient` au lieu de `KimiProvider` (décision passée non appliquée).

**Fix :**
```python
# AVANT (ligne 22)
from app.core.integrations.tavily import TavilyClient
self.tavily_client = TavilyClient()

# APRÈS
from app.core.providers.kimi import KimiProvider
self.kimi_provider = KimiProvider(
    api_key=settings.KIMI_API_KEY,
    model="moonshot-v1-8k"
)

# Ligne 72 - Adapter l'appel
competitive_data = await self.kimi_provider.search(
    query=search_query,
    max_results=10,
    search_depth="basic"
)
```

**Note :** `KimiProvider` déjà implémenté dans `app/core/providers/kimi.py` (443 lignes).

---

### 2️⃣ TemplateAgent - Thèmes IA Élaborés (1-2 jours)

**Fichier :** `app/core/agents/template.py`

**Problème :** Logique basique (4 templates hardcodés, if/else simple) → designs moches.

**Solution :** Refactorer pour utiliser IA :
- Recherche design références via Kimi
- Génération palette couleurs via Deepseek LLM
- Sélection fonts professionnelles
- Style visuel adapté (moderne, élégant, etc.)

**Nouvelle architecture :** Voir détails complets dans `WO-009` section "Tâche 2".

---

### 3️⃣ Stabiliser Tests Backend (4-5h)

**Problèmes :**
- Import `json` manquant dans `tests/test_api/test_coaching.py`
- Erreurs 401 vs 200 (auth mocks incorrects)
- Profile test Docker absent

**Fixes :**
1. Ajouter `import json` ligne 4 de `test_coaching.py`
2. Corriger auth mocks dans `conftest.py`
3. Créer profile test dans `docker-compose.yml`
4. Atteindre 100% pass rate pytest

---

### 4️⃣ Améliorer Exceptions (1-2h)

**Fichier :** `app/utils/exceptions.py`

**Problème :** Trop simpliste (`class GenesisAIException(Exception): pass`)

**Solution :** Structure avec codes erreurs (voir WO-009 Tâche 4)

---

## 📚 Documents à Consulter

**Priorité 1 (Lire en premier) :**
1. `docs/work_orders/WO-009-PHASE2-FINALISATION-25DEC2025.md` - Work order détaillé
2. `docs/PHASE2-STATE-ANALYSIS-25DEC2025.md` - Analyse complète état réel

**Référence (Si besoin) :**
- `app/core/providers/kimi.py` - KimiProvider déjà implémenté
- `app/core/agents/logo.py` - Exemple agent IA complet
- `app/core/agents/seo.py` - Structure à conserver

---

## ⏱️ Planning Suggéré

**Jour 1-2 :** SeoAgent (Kimi) + Début TemplateAgent IA  
**Jour 3-4 :** Finaliser TemplateAgent + Tests backend  
**Jour 5-6 :** Exceptions + Documentation + Validation  

**Total :** 6 jours (8-11 jours si imprévus)

---

## ✅ Validation Finale

**Phase 2 complète si :**
- ✅ SeoAgent utilise Kimi search
- ✅ TemplateAgent génère thèmes IA élaborés (beaux designs)
- ✅ Tests backend 100% pass
- ✅ Profile test Docker fonctionne
- ✅ E2E DC360 → Site avec **design professionnel**

---

## 🚀 Pour Commencer

1. Lire `WO-009-PHASE2-FINALISATION-25DEC2025.md`
2. Lire `PHASE2-STATE-ANALYSIS-25DEC2025.md`
3. Commencer par SeoAgent (fix rapide 2-3h)
4. Enchaîner sur TemplateAgent (plus complexe)

---

**Questions ?** Consulter les work orders ou demander clarifications.

**Deadline :** 6 Janvier 2026  
**Bonne chance ! 💪**
