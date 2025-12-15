# 📋 PLANNING PROJET GENESIS AI - JIRA

**Date de mise à jour :** 30 novembre 2025  
**Préparé par :** Tech Lead Genesis AI  
**Pour :** Principal Architect & Ecosystem Scrum Master (Jira Setup)  
**Status :** ✅ IMPORTÉ DANS JIRA

---

## 🔗 CORRESPONDANCE CLÉS JIRA

> **Note :** La clé projet Jira réelle est `GEN` (et non `GENESIS`).

### Epics
| Réf. Doc | Clé Jira | Lien |
|----------|----------|------|
| EPIC-001 | GEN-1 | [Ouvrir](https://digitalcloud360.atlassian.net/browse/GEN-1) |
| EPIC-002 | GEN-2 | [Ouvrir](https://digitalcloud360.atlassian.net/browse/GEN-2) |
| EPIC-003 | GEN-3 | [Ouvrir](https://digitalcloud360.atlassian.net/browse/GEN-3) |
| EPIC-004 | GEN-4 | [Ouvrir](https://digitalcloud360.atlassian.net/browse/GEN-4) |
| EPIC-005 | GEN-5 | [Ouvrir](https://digitalcloud360.atlassian.net/browse/GEN-5) |
| EPIC-006 | GEN-6 | [Ouvrir](https://digitalcloud360.atlassian.net/browse/GEN-6) |

### Stories Sprint 5
| Réf. Doc | Clé Jira | Lien |
|----------|----------|------|
| GENESIS-020 | GEN-7 | [Ouvrir](https://digitalcloud360.atlassian.net/browse/GEN-7) |
| GENESIS-021 | GEN-8 | [Ouvrir](https://digitalcloud360.atlassian.net/browse/GEN-8) |
| GENESIS-022 | GEN-9 | [Ouvrir](https://digitalcloud360.atlassian.net/browse/GEN-9) |
| GENESIS-023 | GEN-10 | [Ouvrir](https://digitalcloud360.atlassian.net/browse/GEN-10) |
| GENESIS-024 | GEN-11 | [Ouvrir](https://digitalcloud360.atlassian.net/browse/GEN-11) |
| GENESIS-025 | GEN-12 | [Ouvrir](https://digitalcloud360.atlassian.net/browse/GEN-12) |

---

## 📊 VUE D'ENSEMBLE DU PROJET

### Informations Projet
| Champ | Valeur |
|-------|--------|
| **Nom Projet** | Genesis AI |
| **Clé Projet** | **GEN** (Jira) |
| **Type** | Scrum |
| **Sprint Duration** | 2 semaines |
| **Date de Début** | 18 novembre 2025 |
| **Date de Fin Estimée** | 28 février 2026 |

### Équipe
| Rôle | Assigné |
|------|---------|
| Product Owner | Utilisateur Humain |
| Scrum Master / Coordinator | Cascade (Autre session) |
| Tech Lead Genesis | Cascade (Cette session) |
| Tech Lead DC360 | IA Simulée |

---

## 🎯 ÉPICS PRINCIPAUX

### EPIC-001: Socle Technique & Infrastructure
**Status:** ✅ DONE  
**Sprints:** 1-2 (S1-S2)  
**Date Fin:** 27/11/2025

### EPIC-002: Intégration SSO Hub DC360
**Status:** ✅ DONE  
**Sprints:** 3-4 (S3-S4)  
**Date Fin:** 29/11/2025

### EPIC-003: Transformer & Renderer
**Status:** 🔄 IN PROGRESS  
**Sprints:** 4-5 (S4-S5)  
**Date Fin Estimée:** 08/12/2025

### EPIC-004: Intelligence IA (LangGraph + Sub-Agents)
**Status:** ⏳ TO DO  
**Sprints:** 5-8 (S5-S8)  
**Date Fin Estimée:** 05/01/2026

### EPIC-005: Modules Premium (Vocal, Analytics)
**Status:** ⏳ BACKLOG  
**Sprints:** 9-10 (S9-S10)  
**Date Fin Estimée:** 02/02/2026

### EPIC-006: Modules Business (E-commerce, Mobile Money)
**Status:** ⏳ BACKLOG  
**Sprints:** 11-12 (S11-S12)  
**Date Fin Estimée:** 28/02/2026

---

## 📅 DÉTAIL PAR SPRINT

---

## SPRINT 1-2 (S1-S2) | ✅ CLÔTURÉ
**Dates:** 18/11 - 01/12/2025  
**Objectif:** Socle Technique Genesis AI

### Stories Complétées

| ID | Story | Points | Status |
|----|-------|--------|--------|
| GENESIS-001 | Infrastructure FastAPI + Docker | 8 | ✅ Done |
| GENESIS-002 | Authentification JWT fonctionnelle | 5 | ✅ Done |
| GENESIS-003 | Orchestrateur LangGraph Core | 8 | ✅ Done |
| GENESIS-004 | Providers LLM (Deepseek, Kimi, DALL-E) | 8 | ✅ Done |
| GENESIS-005 | Redis Virtual File System | 5 | ✅ Done |
| GENESIS-006 | 5 Sub-Agents (Research, Content, Logo, SEO, Template) | 13 | ✅ Done |
| GENESIS-007 | Tests Unitaires + Smoke (27 tests) | 5 | ✅ Done |

**Vélocité Sprint 1-2:** 52 points

---

## SPRINT 3-4 (S3-S4) | ✅ CLÔTURÉ
**Dates:** 02/12 - 15/12/2025 (effectif: 27/11 - 29/11)  
**Objectif:** Frontend Autonome + SSO Hub DC360

### Stories Complétées

| ID | Story | Points | Status |
|----|-------|--------|--------|
| GENESIS-010 | Frontend Next.js 14 + TypeScript + Tailwind | 8 | ✅ Done |
| GENESIS-011 | Landing Page Genesis | 3 | ✅ Done |
| GENESIS-012 | Interface Chat Split-Screen | 5 | ✅ Done |
| GENESIS-013 | SSO Token Passing (AuthContext.tsx) | 8 | ✅ Done |
| GENESIS-014 | API Routes /auth/validate & /auth/me | 5 | ✅ Done |
| GENESIS-015 | Docker Network dc360-ecosystem-net | 3 | ✅ Done |
| GENESIS-016 | Tests E2E SSO (chrome-devtools) | 5 | ✅ Done |
| GENESIS-017 | Documentation & Memos SSO | 2 | ✅ Done |

**Vélocité Sprint 3-4:** 39 points

---

## SPRINT 5 (S5) | 🔄 EN COURS
**Dates:** 30/11 - 13/12/2025  
**Objectif:** Transformer & Block Renderer

### Stories Sprint Actuel

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| GENESIS-020 | Transformer: Algorithme Brief → SiteDefinition | 8 | Tech Lead Genesis | 🔄 In Progress |
| GENESIS-021 | SiteDefinition JSON Schema | 3 | Tech Lead Genesis | ⏳ To Do |
| GENESIS-022 | Block Renderer: Composants React Dynamiques | 8 | Tech Lead Genesis | ⏳ To Do |
| GENESIS-023 | Intégration Transformer ↔ Backend FastAPI | 5 | Tech Lead Genesis | ⏳ To Do |
| GENESIS-024 | Page /preview pour affichage site généré | 5 | Tech Lead Genesis | ⏳ To Do |
| GENESIS-025 | Tests E2E: Brief → Site visible | 5 | Tech Lead Genesis | ⏳ To Do |

**Capacité Sprint 5:** 34 points

### Critères d'Acceptation Sprint 5
- [ ] Utilisateur génère brief via chat
- [ ] Clic "Voir mon site" → Landing Page complète affichée
- [ ] Site structuré selon secteur d'activité (plombier, restaurant, etc.)
- [ ] Mapping déterministe Brief → SiteDefinition (IA créative en Phase 2)

---

## SPRINT 6-7 (S6-S7) | ⏳ PLANIFIÉ
**Dates:** 14/12 - 27/12/2025  
**Objectif:** Intelligence IA - Remplacement Mock par LangGraph

### Stories Planifiées

| ID | Story | Points | Status |
|----|-------|--------|--------|
| GENESIS-030 | Intégration Orchestrateur LangGraph dans Chat | 8 | ⏳ To Do |
| GENESIS-031 | Connexion RedisVFS pour génération fichiers réels | 5 | ⏳ To Do |
| GENESIS-032 | Activation Research Sub-Agent (Tavily API) | 5 | ⏳ To Do |
| GENESIS-033 | Activation Content Sub-Agent (génération contenu) | 5 | ⏳ To Do |
| GENESIS-034 | Activation Logo Sub-Agent (DALL-E 3) | 5 | ⏳ To Do |
| GENESIS-035 | Workflow Coaching 5 Étapes UI | 8 | ⏳ To Do |
| GENESIS-036 | Persistance Session Coaching (Redis TTL 2h) | 3 | ⏳ To Do |
| GENESIS-037 | Tests Intégration LangGraph E2E | 5 | ⏳ To Do |

**Capacité Sprint 6-7:** 44 points

---

## SPRINT 8 (S8) | ⏳ PLANIFIÉ
**Dates:** 28/12/2025 - 10/01/2026  
**Objectif:** Finalisation Phase 2 + SEO/Template Agents

### Stories Planifiées

| ID | Story | Points | Status |
|----|-------|--------|--------|
| GENESIS-040 | Activation SEO Sub-Agent (Optimisation locale) | 5 | ⏳ To Do |
| GENESIS-041 | Activation Template Sub-Agent (Sélection intelligente) | 5 | ⏳ To Do |
| GENESIS-042 | Génération Business Brief Final | 8 | ⏳ To Do |
| GENESIS-043 | Performance < 45min workflow total | 3 | ⏳ To Do |
| GENESIS-044 | Monitoring & Health Checks Complets | 3 | ⏳ To Do |
| GENESIS-045 | Documentation Technique Phase 2 | 2 | ⏳ To Do |

**Capacité Sprint 8:** 26 points

---

## SPRINT 9-10 (S9-S10) | ⏳ BACKLOG
**Dates:** 11/01 - 07/02/2026  
**Objectif:** Modules Premium (Phase 3A)

### Stories Backlog

| ID | Story | Points | Module | Status |
|----|-------|--------|--------|--------|
| GENESIS-050 | Module Vocal (Speech-to-Text + TTS) | 13 | Communication | ⏳ Backlog |
| GENESIS-051 | Analytics IA (Tracking éthique) | 8 | Business | ⏳ Backlog |
| GENESIS-052 | Domaine Personnalisé (DNS Config) | 5 | Growth | ⏳ Backlog |
| GENESIS-053 | Module Multi-langue (fr, en, wo) | 5 | Communication | ⏳ Backlog |
| GENESIS-054 | pgvector Integration (Mémoire Sémantique) | 8 | Core | ⏳ Backlog |
| GENESIS-055 | Module Registry UI (Activation/Désactivation) | 5 | Core | ⏳ Backlog |

**Estimation Sprint 9-10:** 44 points

---

## SPRINT 11-12 (S11-S12) | ⏳ BACKLOG
**Dates:** 08/02 - 28/02/2026  
**Objectif:** Modules Business (Phase 3B)

### Stories Backlog

| ID | Story | Points | Module | Status |
|----|-------|--------|--------|--------|
| GENESIS-060 | E-commerce Module (Catalogue Produits) | 13 | Business | ⏳ Backlog |
| GENESIS-061 | Mobile Money Integration (Wave, Orange Money) | 8 | Business | ⏳ Backlog |
| GENESIS-062 | Blog IA (Génération articles automatique) | 8 | Growth | ⏳ Backlog |
| GENESIS-063 | SEO Boost Module (Méta-tags, Sitemap) | 5 | Growth | ⏳ Backlog |
| GENESIS-064 | Booking Module (Calendrier RDV) | 8 | Business | ⏳ Backlog |
| GENESIS-065 | Templates Premium (5 nouveaux templates) | 5 | Design | ⏳ Backlog |

**Estimation Sprint 11-12:** 47 points

---

## 📈 MÉTRIQUES & KPIs PROJET

### Burndown Chart Data
| Sprint | Planifié | Réalisé | Vélocité |
|--------|----------|---------|----------|
| S1-S2 | 55 | 52 | 52 |
| S3-S4 | 40 | 39 | 39 |
| S5 | 34 | - | - |
| S6-S7 | 44 | - | - |
| S8 | 26 | - | - |

**Vélocité Moyenne:** ~45 points/2-sprints

### KPIs Produit (Cibles)
| Phase | ARPU Cible | Users avec Extensions |
|-------|------------|----------------------|
| Phase 1 (S1-S4) | 2.500 FCFA | 20% |
| Phase 2 (S5-S8) | 8.000 FCFA | 40% |
| Phase 3 (S9-S12) | 15.000 FCFA | 60% |

---

## 🏷️ LABELS JIRA SUGGÉRÉS

### Par Composant
- `frontend` - Travail Next.js/React
- `backend` - Travail FastAPI
- `infrastructure` - Docker, DevOps
- `ai-agent` - LangGraph, Sub-Agents
- `integration` - APIs externes (DC360, Tavily, etc.)

### Par Type
- `feature` - Nouvelle fonctionnalité
- `bug` - Correction de bug
- `tech-debt` - Dette technique
- `security` - Sécurité
- `documentation` - Docs et memos

### Par Module (Phase 3)
- `module-vocal` - Extension Vocal
- `module-analytics` - Extension Analytics
- `module-ecommerce` - Extension E-commerce
- `module-payment` - Mobile Money

### Par Priorité
- `critical` - Bloquant
- `high` - Priorité haute
- `medium` - Priorité normale
- `low` - Nice-to-have

---

## 🔗 DÉPENDANCES INTER-PROJETS

### Genesis ↔ DC360 Hub
| Dépendance | Direction | Status |
|------------|-----------|--------|
| SSO Token Passing | DC360 → Genesis | ✅ Opérationnel |
| User Profile API | DC360 → Genesis | ✅ Opérationnel |
| Billing Integration | DC360 → Genesis | ⏳ Phase 3 |
| Module Registry Sync | Genesis ↔ DC360 | ⏳ Phase 3 |

### APIs Externes
| API | Usage | Status |
|-----|-------|--------|
| OpenAI (GPT-4o) | LLM Fallback | ✅ Configuré |
| Deepseek | LLM Primary | ✅ Opérationnel |
| Kimi (Moonshot) | Search + LLM | ✅ Opérationnel |
| DALL-E 3 | Logo Generation | ✅ Opérationnel |
| Tavily | Search Fallback | ✅ Configuré |

---

## 📝 NOTES POUR IMPORT JIRA

### Structure Recommandée
```
Projet: GENESIS
├── Epic: EPIC-001 Socle Technique
│   ├── Story: GENESIS-001
│   ├── Story: GENESIS-002
│   └── ...
├── Epic: EPIC-002 SSO Integration
│   ├── Story: GENESIS-010
│   └── ...
├── Epic: EPIC-003 Transformer & Renderer (CURRENT)
│   ├── Story: GENESIS-020
│   └── ...
└── ...
```

### Champs Personnalisés Suggérés
- **Module** (dropdown): Core, Communication, Business, Growth, Design
- **Phase** (dropdown): Phase 1A, Phase 1B, Phase 2, Phase 3
- **Security Impact** (checkbox): Impacte la sécurité
- **API Dependency** (text): API externe requise

### Workflow Suggéré
```
To Do → In Progress → Code Review → Testing → Done
```

### Définition of Done (DoD)
- [ ] Code implémenté et testé
- [ ] Tests unitaires passent
- [ ] Code review approuvé
- [ ] Documentation mise à jour
- [ ] Déployé en staging
- [ ] Tests E2E validés

---

## 🚀 ACTIONS IMMÉDIATES

### Pour le Scrum Master (Jira Setup)
1. **Créer le projet GENESIS** dans Jira (Scrum template)
2. **Créer les 6 Epics** listés ci-dessus
3. **Créer le Sprint 5** (30/11 - 13/12/2025)
4. **Importer les stories GENESIS-020 à GENESIS-025** dans Sprint 5
5. **Configurer les labels** suggérés
6. **Créer le Board Scrum** avec swimlanes par Epic

### Pour le Tech Lead Genesis
1. **Commencer GENESIS-020** (Transformer)
2. **Daily standups** avec update Jira
3. **Demo fin de Sprint 5** le 13/12/2025

---

**Document prêt pour import Jira.**

*Tech Lead Genesis AI - 30/11/2025*
