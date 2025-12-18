---
title: "Work Order Phase 2 - Sprint 6"
date: "2025-12-18"
sprint: 6
phase: "2"
status: "En Cours"
tags: ["genesis", "phase2", "langgraph", "vocal", "pgvector"]
---

# 📋 Work Order — Phase 2 Sprint 6

## 🎯 Objectif Sprint 6

> **Activer l'IA conversationnelle réelle** : Remplacer le mock chat par le LangGraph Orchestrator avec les 5 sub-agents fonctionnels.

---

## 📊 État Actuel (Post Phase 1B)

### Infrastructure Existante
- ✅ LangGraph Orchestrator (`langgraph_orchestrator.py`) — 299 lignes
- ✅ ResearchSubAgent — Analyse marché multi-provider (Tavily/Kimi + Deepseek)
- ✅ ContentSubAgent — Génération contenu multilingue
- ✅ LogoAgent — Intégration LogoAI
- ✅ SeoAgent — Optimisation SEO via Tavily
- ✅ TemplateAgent — Sélection templates

### Problème Actuel
Le endpoint `/api/v1/chat` utilise un **mock** qui détecte le mot "site" :
```python
# Comportement actuel (mock)
if "site" in message.lower():
    return "J'ai bien compris... Je génère votre site..."
```

---

## 🔧 Stories Sprint 6

### GEN-13: Connecter LangGraph au Chat Endpoint
**Priorité:** 🔴 Haute | **Effort:** 3 points

**Description:**
Remplacer la logique mock du chat par l'appel réel au LangGraph Orchestrator.

**Critères d'acceptation:**
- [ ] Le chat appelle `LangGraphOrchestrator.run()` quand l'utilisateur décrit son business
- [ ] Les 5 sub-agents s'exécutent en parallèle (research → [content, logo, seo, template])
- [ ] Le résultat est transformé en SiteDefinition
- [ ] Le site généré est affiché dans le preview
- [ ] Fallback gracieux si un agent échoue

**Fichiers à modifier:**
- `app/api/v1/chat.py`
- `app/api/v1/sites.py`
- `app/services/transformer.py`

---

### GEN-14: Input Vocal (Web Speech API)
**Priorité:** 🟡 Moyenne | **Effort:** 5 points

**Description:**
Permettre à l'utilisateur de dicter son business brief par la voix.

**Critères d'acceptation:**
- [ ] Bouton microphone dans l'interface chat
- [ ] Transcription en temps réel (Web Speech API)
- [ ] Support français + langues africaines (wolof, bambara)
- [ ] Indicateur visuel d'écoute
- [ ] Fallback texte si micro non disponible

**Fichiers à créer:**
- `genesis-frontend/src/components/VoiceInput.tsx`
- `genesis-frontend/src/hooks/useSpeechRecognition.ts`

---

### GEN-15: pgvector - Mémoire Sémantique
**Priorité:** 🟡 Moyenne | **Effort:** 5 points

**Description:**
Ajouter une mémoire sémantique pour personnaliser les recommandations basées sur l'historique utilisateur.

**Critères d'acceptation:**
- [ ] Extension pgvector installée dans PostgreSQL
- [ ] Table `user_embeddings` pour stocker les vecteurs
- [ ] Embedding des business briefs générés
- [ ] Recherche similarité pour recommandations
- [ ] API endpoint `/api/v1/memory/similar`

**Fichiers à créer:**
- `app/core/memory/vector_store.py`
- `app/models/embedding.py`
- Migration Alembic pour pgvector

---

## 📅 Planning Sprint 6

| Jour | Story | Tâches |
|------|-------|--------|
| J1 | GEN-13 | Analyse chat.py, connexion orchestrator |
| J2 | GEN-13 | Transformation résultat → SiteDefinition |
| J3 | GEN-13 | Tests E2E, fix bugs |
| J4 | GEN-14 | Composant VoiceInput, hook |
| J5 | GEN-14 | Intégration chat, tests |
| J6 | GEN-15 | Setup pgvector, migrations |
| J7 | GEN-15 | Vector store, API endpoint |

---

## 🏗️ Architecture Cible Phase 2

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ VoiceInput   │  │ ChatInterface│  │ BlockRenderer│       │
│  │ (Web Speech) │──│              │──│ (10 blocks)  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API (FastAPI)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ /chat        │──│ /sites       │──│ /memory      │       │
│  │ (real AI)    │  │ /generate    │  │ /similar     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Orchestrator                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────┐│
│  │Research │  │Content  │  │Logo     │  │SEO      │  │Templ││
│  │SubAgent │  │SubAgent │  │Agent    │  │Agent    │  │Agent││
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ PostgreSQL   │  │ pgvector     │  │ Redis        │       │
│  │ (users,sites)│  │ (embeddings) │  │ (cache,VFS)  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Démarrage Immédiat

**Commencer par GEN-13** : C'est le coeur de la Phase 2 — activer l'IA réelle dans le chat.

```bash
# Fichier principal à modifier
c:\genesis\app\api\v1\chat.py
```

---

*Tech Lead Genesis AI*  
*18 décembre 2025*
