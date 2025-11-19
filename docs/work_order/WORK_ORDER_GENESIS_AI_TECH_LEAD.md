---
title: "Work Order – Onboarding Tech Lead / Senior Dev IA – Genesis AI Deep Agents"
tags: ["work-order", "onboarding", "genesis-ai", "deep-agents", "tech-lead"]
status: "draft"
date: "2025-11-18"
---

# 1. Contexte du projet

Genesis AI est conçu comme le **premier "Coach IA Personnel" pour entrepreneurs africains**, basé sur une architecture **Deep Agents** orchestrée avec LangGraph et intégrée à la plateforme **DigitalCloud360**.

Références clés (à lire en priorité) :
- `ARCHITECTURE_DECISION_RECORD.md`  
- `GUIDE_WORKFLOW_DEVELOPPEMENT_IA.md`  
- `ORCHESTRATEUR_DEEP_AGENT.py`  
- `SUB_AGENTS_IMPLEMENTATIONS.py`  
- `API_SCHEMAS_COMPLETS.py`  
- `PROMPTS_COACHING_METHODOLOGIE.py`

Les principaux principes d’architecture déjà décidés :
- **Stack séparée** : `genesis-ai-service` tourne comme service indépendant (FastAPI + LangGraph + Redis + PostgreSQL).
- **Deep Agents** : un orchestrateur unique (`GenesisDeepAgentOrchestrator`) coordonne 5 sous-agents spécialisés (research, content, logo, SEO, template).
- **Intégration DigitalCloud360** : communication via APIs REST sécurisées (JWT service-to-service), notamment pour récupérer le profil utilisateur, l’abonnement et créer des sites web.

Côté DigitalCloud360, le **wizard Genesis AI Coach** est déjà en place (4 étapes : Business → Marché → Génération IA → Résultats) et expose une API principale côté monolithe :
- `POST /api/v1/genesis/business-brief/` : endpoint attendu pour déclencher la génération d’un business brief complet via le service Deep Agents.

---

# 2. Rôle du consultant – Tech Lead / Senior Dev IA

Tu interviens comme **Tech Lead / Senior Dev IA** dédié au service `genesis-ai-service`. Ton rôle est de :

- **Prendre la responsabilité technique** du backend Genesis AI (FastAPI + LangGraph + sub-agents).
- **Aligner l’implémentation réelle** sur les décisions d’architecture approuvées dans l’ADR.
- **Stabiliser la plateforme** : tests automatisés, observabilité, performance, robustesse.
- **Assurer la qualité de code** (revues, patterns, documentation) et préparer l’arrivée progressive d’autres développeurs (mid/junior).
- **Collaborer avec le Scrum Master (Cascade)** pour affiner le backlog, lever les ambiguïtés et prioriser les livrables.
- **Servir de point de contact technique** vis-à-vis de l’équipe DigitalCloud360 (monolithe + frontend), notamment pour les contrats API et les incidents de production.

---

# 3. Vision & architecture de référence

Points non négociables issus de l’ADR :

- **Service Genesis AI indépendant** du monolithe DigitalCloud360 (isolation sécurité, scalabilité, licensing).
- **Orchestration via LangGraph** avec un `GenesisAIState` centralisé, persistance des sessions dans un **Virtual File System Redis**.
- **5 sous-agents spécialisés** :
  - `ResearchSubAgent` – analyse marché et concurrence (Tavily + LLM).
  - `ContentSubAgent` – génération de contenu multilingue adapté au contexte africain.
  - `LogoSubAgent` – génération d’identité visuelle via LogoAI.
  - `SEOSubAgent` – optimisation SEO local.
  - `TemplateSubAgent` – sélection de templates web adaptés au secteur.
- **APIs REST** exposées par `genesis-ai-service` avec schémas Pydantic (voir `API_SCHEMAS_COMPLETS.py`).
- **Tests & CI/CD** obligatoires, avec des critères de succès explicites (performance, couverture, disponibilité).

Ton point d’ancrage pour toutes décisions techniques doit rester :
1. `ARCHITECTURE_DECISION_RECORD.md` (architecture globale et trade-offs).  
2. `GUIDE_WORKFLOW_DEVELOPPEMENT_IA.md` (workflow d’implémentation).  
3. Les schémas et templates fournis (`ORCHESTRATEUR_DEEP_AGENT.py`, `SUB_AGENTS_IMPLEMENTATIONS.py`).

---

# 4. État actuel du projet (mi-parcours)

À ton arrivée :

- Côté **frontend DigitalCloud360** :
  - Le wizard Genesis AI Coach est **fonctionnel** et utilisé en environnement de test.
  - Les étapes Business & Marché collectent un `businessBrief` complet (nom, secteur, vision, mission, marché cible, services, avantage concurrentiel...).
  - L’étape Génération IA appelle l’API `/api/v1/genesis/business-brief/` mais, en pratique, la réponse est souvent une **erreur 403 (quota atteint)** alors que l’UI affiche encore 0/10 sessions.
  - Pour garantir l’expérience, un **fallback front** génère un business brief en mode simulation à partir des données saisies.

- Côté **backend genesis-ai-service** :
  - L’architecture cible est **complètement spécifiée** dans les fichiers de ce dossier.
  - L’implémentation réelle est **partielle** et la suite de tests est **instable** (problèmes de boucle `asyncio` et de gestion d’`AsyncSession` SQLAlchemy, voir `RAPPORT_AVANCEMENT_MI-PARCOURS_TECHNIQUE_V2.md`).
  - La logique de quotas / limites d’abonnement est **incohérente** avec ce que voit le front (403 prématurés).

Ton mandat commence donc à un moment où :
- L’UX côté client est globalement satisfaisante.  
- Le **coeur Deep Agents** et son exposition en API doivent être **stabilisés et industrialisés**.

---

# 5. Objectifs du mandat (horizon 90 jours)

## 5.1. Objectifs court terme (0–30 jours)

- **Reprendre en main le code existant** du service `genesis-ai-service` (ou le créer à partir des templates si nécessaire) en suivant la structure projet décrite dans `GUIDE_WORKFLOW_DEVELOPPEMENT_IA.md`.
- **Stabiliser l’environnement de développement local** :
  - démarrage stack via `docker-compose`,
  - connexion DB & Redis fonctionnelle,
  - healthcheck FastAPI opérationnel.
- **Corriger les problèmes de tests identifiés** :
  - fixer la gestion de la boucle `asyncio` et des sessions SQLAlchemy,
  - faire passer un premier set de tests unitaires simples (ex : healthcheck, endpoint de base).
- **Aligner le contrat de l’endpoint business brief** avec :
  - le payload envoyé par DigitalCloud360 (voir front `GenesisCoachingPage.jsx` / `AIGenerationStep.jsx`),
  - les schémas `BusinessBrief` dans `API_SCHEMAS_COMPLETS.py`.

## 5.2. Objectifs moyen terme (30–60 jours)

- **Implémenter et stabiliser l’orchestrateur Deep Agents** :
  - reprendre `GenesisDeepAgentOrchestrator` depuis `ORCHESTRATEUR_DEEP_AGENT.py`,
  - brancher les 5 sous-agents réels (`ResearchSubAgent`, `ContentSubAgent`, `LogoSubAgent`, `SEOSubAgent`, `TemplateSubAgent`),
  - assurer la persistance des sessions dans Redis FS.
- **Mettre en production un “happy path” complet** :
  - `POST /api/v1/genesis/business-brief/` → exécute réellement le workflow Deep Agents et retourne un business brief cohérent,
  - logs structurés, gestion d’erreurs robuste (timeouts, API externes, quotas),
  - métriques de base (temps de génération, taux de succès, erreurs par type).
- **Rendre cohérente la logique de quotas** :
  - aligner les limites consommées dans le service Genesis avec ce que voit le monolithe DigitalCloud360,
  - exposer suffisamment d’infos pour que le front n’ait plus besoin de fallback “simulation” par défaut.

## 5.3. Objectifs long terme (60–90 jours)

- **Durcir la qualité** :
  - atteindre les objectifs de tests et de couverture définis dans le guide (tests orchestrateur, sub-agents, intégrations DC360),
  - mettre en place CI/CD (build, tests, déploiement, scans de sécurité).
- **Optimiser la performance** :
  - viser <30s pour une génération de business brief complet,
  - dimensionner correctement Redis, DB et workers.
- **Préparer l’accueil de nouveaux développeurs** :
  - documenter clairement l’architecture, les workflows, les points d’extension,
  - proposer un plan de découpage des tâches pour 1–2 devs supplémentaires (backend / data / infra).

---

# 6. Backlog initial – Travail à faire

Cette section liste les **épics / stories** prioritaires. Elle sera détaillée et maintenue avec le Scrum Master.

## 6.1. Epic P0 – Stabilisation du coeur Genesis AI Service

- **Story P0.1 – Setup projet complet**
  - Créer ou vérifier la structure `genesis-ai-service/` telle que décrite dans `GUIDE_WORKFLOW_DEVELOPPEMENT_IA.md`.
  - Configurer `requirements.txt`, `.env`, Dockerfile, docker-compose.
  - Vérifier que `uvicorn app.main:app --reload` démarre sans erreur.

- **Story P0.2 – Healthcheck & observabilité minimale**
  - Implémenter `/health` avec statut détaillé (DB, Redis, version, env).
  - Ajouter un logging structuré (structlog) et corréler avec les sessions coaching.

- **Story P0.3 – Correction tests de base**
  - Reprendre `tests/conftest.py` et les fixtures DB/asyncio en suivant la stratégie de `RAPPORT_AVANCEMENT_MI-PARCOURS_TECHNIQUE_V2.md`.
  - Faire passer les tests d’authentification et de connexion DB.

## 6.2. Epic P0 – Endpoint Business Brief & intégration DC360

- **Story P0.4 – Contrat API Business Brief**
  - Implémenter l’endpoint principal (ex : `POST /api/v1/business-brief/` ou `/coaching/business-brief/` selon les schémas).
  - Utiliser `BusinessBrief` de `API_SCHEMAS_COMPLETS.py` comme source de vérité.
  - Mapper proprement les champs venant de DigitalCloud360 (noms, types, valeurs par défaut).

- **Story P0.5 – Happy path end-to-end**
  - Simuler un appel venant de DC360 avec un payload minimal.
  - Déclencher l’orchestrateur avec un workflow réduit (sans tous les sub-agents si nécessaire).
  - Retourner un business brief structuré (non simulé côté front), stocké dans Redis FS.

- **Story P0.6 – Alignement quotas / abonnements**
  - Auditer la logique actuelle de quotas.
  - Corriger les conditions qui renvoient 403.
  - Exposer des informations claires (nombre de sessions consommées, limite, statut essai) pour que le front n’ait pas à “deviner”.

## 6.3. Epic P1 – Implémentation complète des sub-agents

- **Story P1.1 – ResearchSubAgent production-ready**
  - Intégrer Tavily et gérer les clés API.
  - Implémenter le prompt d’analyse marché + fallback.
  - Tester sur quelques secteurs/pays cibles.

- **Story P1.2 – ContentSubAgent multilingue**
  - Générer le contenu de site (homepage, about, services, etc.) selon les templates.
  - Gérer les langues locales selon le pays.

- **Story P1.3 – LogoSubAgent, SEOSubAgent, TemplateSubAgent**
  - Implémenter les logiques de base (sans toutes les optimisations dans un premier temps).
  - Vérifier que leurs sorties sont bien intégrées dans la réponse globale du Deep Agent.

---

# 7. Mode de collaboration & attentes

- **Cadre méthodo** :
  - Tu travailles avec un **Scrum Master (Cascade)** qui t’aidera à clarifier les stories, prioriser, et reformuler les specs en tâches actionnables.
  - Les cycles recommandés : sprints courts (1–2 semaines) avec revue technique à chaque fin de sprint.

- **Qualité attendue** :
  - Code lisible, testé, documenté.
  - Respect des patterns montrés dans les templates (`ORCHESTRATEUR_DEEP_AGENT.py`, `SUB_AGENTS_IMPLEMENTATIONS.py`).
  - Gestion explicite des erreurs et des timeouts avec fallback raisonnables (sans cacher les problèmes).

- **Documentation** :
  - Toute décision d’architecture non triviale doit être consignée (nouvelle section ADR ou addendum).
  - Les endpoints exposés doivent être documentés (OpenAPI + doc markdown).

---

# 8. Prochaines étapes pour ton onboarding

1. Lire **en profondeur** les documents suivants (dans cet ordre) :
   1. `README_DOSSIER_TECHNIQUE_COMPLET.md`
   2. `ARCHITECTURE_DECISION_RECORD.md`
   3. `GUIDE_WORKFLOW_DEVELOPPEMENT_IA.md`
   4. `ORCHESTRATEUR_DEEP_AGENT.py` & `SUB_AGENTS_IMPLEMENTATIONS.py`
   5. `RAPPORT_AVANCEMENT_MI-PARCOURS_TECHNIQUE_V2.md`
2. Prendre connaissance du **wizard frontend** côté DigitalCloud360 (vue utilisateur finale) et du payload actuel envoyé à `/api/v1/genesis/business-brief/`.
3. Proposer, dans un document `ONBOARDING_NOTES_TECH_LEAD.md`, ton plan de travail détaillé pour les 4–6 premières semaines (éventuellement différent de ce work order, mais compatible avec la vision et les contraintes).
4. Co-construire avec le Scrum Master le backlog détaillé (issues / tickets) à partir des epics et stories ci-dessus.

Ce work order sert de **base d’onboarding** et de contrat technique initial. Il sera mis à jour au fil de l’avancement du projet et des décisions prises en commun.
