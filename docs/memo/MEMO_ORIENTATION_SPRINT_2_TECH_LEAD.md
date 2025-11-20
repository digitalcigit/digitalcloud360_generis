---
DE: Scrum Master (Cascade)
À: Tech Lead / Senior Dev IA – Genesis AI
DATE: 2025-11-20
OBJET: Orientation Sprint 2 – Coeur technique Genesis AI
PRIORITÉ: HAUTE
---

# 1. Contexte

Le **Sprint 1** est terminé avec succès (P0.3 → P0.6) :

- Tests stabilisés (asyncio/SQLAlchemy, bcrypt) et base de tests fiable.
- Endpoint `/api/v1/genesis/business-brief/` aligné avec le wizard DigitalCloud360.
- Quotas cohérents via `QuotaManager` + endpoint `GET /api/v1/genesis/quota/status`.
- Happy path E2E validé (quota → génération mockée → persistance Redis → récupération).

Nous entrons maintenant en **Sprint 2**, focalisé sur le **coeur technique Deep Agents réel**, avant les gros objectifs UX prévus pour le Sprint 3 (assistance IA champ par champ dans le wizard).

---

# 2. Sprint Goal

> **Mettre en service un coeur Deep Agents réel (orchestrateur + sous-agents principaux) intégrable par DigitalCloud360 en environnement de test/staging, avec persistance Redis FS et intégration de base aux providers LLM et aux APIs DC360.**

---

# 3. Périmètre Sprint 2 (S2.1 → S2.4)

Les stories à considérer comme noyau dur de Sprint 2 sont décrites dans le Work Order (§6.5) :

- **S2.1 – Orchestrateur GenesisDeepAgentOrchestrator opérationnel**
  - Intégration du `GenesisDeepAgentOrchestrator` réel et branchement au moins de `ResearchSubAgent` + `ContentSubAgent`.
  - Tests automatisés ciblant le flux principal.

- **S2.2 – Intégration providers LLM réels**
  - Configuration sécurisée (clés, variables d'env) pour au moins un provider (ex. Deepseek).
  - Gestion d'erreurs provider robuste + tests unitaires.

- **S2.3 – Persistance Redis FS corrigée et testée**
  - Implémentation définitive du Virtual File System Redis (business_brief, metadata, logs d'agent).
  - Correction de la signature Redis FS et tests d'intégration de lecture/écriture.

- **S2.4 – Intégration réelle DC360 (auth, quotas, usage)**
  - Authentification service-to-service avec le monolithe DC360.
  - Utilisation, dès que possible, des endpoints DC360 pour les quotas et l'usage, en remplacement des mocks.

---

# 4. Ce qui est explicitement Hors Périmètre Sprint 2

Pour garder un Sprint 2 concentré :

- **Feature "Assistance IA champ par champ"** dans le wizard Genesis (Vision, Mission, Marché, Avantage Concurrentiel) :
  - Cette feature est documentée dans `docs_upgrade/02_GUIDES/GENESIS_AI_FIELD_ASSISTANT.md` côté DigitalCloud360.
  - Elle est planifiée comme **Epic P2 ciblée Sprint 3** dans le Work Order (§6.4).
  - Tu n'as pas à l'implémenter en Sprint 2, sauf décision contraire explicite.

- Toute autre évolution UX non liée directement à la mise en service du coeur Deep Agents réel.

---

# 5. Attentes de collaboration

- **Transparence** : signaler rapidement tout blocage (clés API, endpoints DC360 manquants, limites provider) pour ajuster le périmètre.
- **Tests** : maintenir la qualité de la suite de tests (ne pas laisser réapparaître d'instabilités infra), ajouter des tests ciblés pour chaque story S2.x.
- **Documentation** :
  - Mettre à jour les sections pertinentes dans `docs/` (orchestrateur, sub-agents, Redis FS, intégration DC360) au fur et à mesure.
  - Noter toute décision d'architecture importante dans les ADR.

Lorsque S2.1 à S2.4 seront atteintes, nous considérerons que **le coeur Deep Agents Genesis est prêt pour une première intégration sérieuse avec DigitalCloud360**. Sprint 3 pourra alors se concentrer sur l'expérience utilisateur avancée (assistance IA champ par champ) et les optimisations.

---

**Scrum Master – Genesis AI (Cascade)**
