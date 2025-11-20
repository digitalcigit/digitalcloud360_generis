---
DE: Scrum Master (Cascade)
À: Tech Lead Genesis AI
DATE: 2025-11-20
OBJET: Réponse au mémo – Priorités, quotas, orchestrateur & périmètre sprint
PRIORITÉ: HAUTE
---

# MEMO – Directives Scrum Master

## 1. Priorités immédiates (ordre à suivre)

1. **P0.3 – Correction fixtures tests (en premier)**
   - Objectif: rendre la suite de tests **prévisible et stable**, même si incomplète.
   - Raison: sans base de tests fiable, tout le reste (endpoint, quotas) reste fragile.
   - Attendu:
     - Plus de `RuntimeError`/`InterfaceError` liés à `asyncio` + `AsyncSession`.
     - `pytest` doit pouvoir s’exécuter intégralement en local sans crash (il peut encore y avoir des tests rouge sur des cas métier, mais pas pour des raisons d’infrastructure/loop).

2. **P0.4 – Alignement endpoint Business Brief (immédiatement après P0.3)**
   - Une fois les tests stabilisés, prioriser l’alignement de l’endpoint Business Brief pour débloquer les intégrations frontend.
   - Cible:
     - Aligner l’endpoint existant `/api/v1/business/brief/generate` sur le contrat attendu **`/api/v1/genesis/business-brief/`**.
     - Utiliser `BusinessBrief` de `API_SCHEMAS_COMPLETS.py` comme **source de vérité**.
     - Garantir que le payload envoyé par le wizard Genesis (DigitalCloud360) est accepté sans erreur de validation.

3. **P0.5 – Logique quotas cohérente (après P0.4, même sprint)**
   - Une fois l’endpoint aligné, ajuster la logique de quotas pour éviter les 403 prématurés.
   - Cible:
     - Plus de situation où le frontend voit « 0/10 sessions » mais le backend renvoie déjà `403 limit reached`.

4. **P0.6 – Tests end-to-end basiques (fin de sprint)**
   - Mettre en place un **happy path minimal**:
     - Appel API → orchestration (même partielle) → business brief structuré → persistance Redis FS.

**Conclusion priorités**: ton plan proposé pour Semaine 1 (P0.3 → P0.4 → P0.5 → P0.6) est **validé**, avec l’insistance forte sur **P0.3 en premier**.

---

## 2. Spécification logique de quotas (P0.5)

### 2.1. Règles métier cibles (version 1)

- **Unité de quota**: nombre de **sessions Genesis AI complètes démarrées** par **utilisateur**.
- **Période de mesure**: mois calendaire (reset le 1er de chaque mois, aligné avec DigitalCloud360).
- **Plans (version actuelle)**:
  - Plan **Genesis AI Basic**: 10 sessions / mois / utilisateur.
  - Plan **Genesis AI Pro**: 50 sessions / mois / utilisateur.
  - Plan **Genesis AI Enterprise**: sessions illimitées.
  - **Essai**: 3 sessions gratuites (puis blocage).
- **Source de vérité**:
  - DigitalCloud360 (monolithe) reste **source de vérité des abonnements et des limites**.
  - Le service `genesis-ai-service` ne doit pas réinventer la logique métier des plans, mais {
    }s’appuyer sur les informations renvoyées par DC360.

### 2.2. Implémentation attendue côté `genesis-ai-service`

- Lorsqu’une nouvelle session de coaching est demandée :
  1. Le service doit disposer, via l’appel entrant ou une intégration, des informations suivantes :
     - `user_id` ou identifiant unique utilisateur.
     - Informations d’abonnement ou au moins un indicateur `can_start_session` + compteurs (`current_usage`, `max_monthly_sessions`), si disponibles.
  2. **Si DigitalCloud360 expose déjà ces informations** via APIs (préféré) :
     - Utiliser le client `DigitalCloud360APIClient` décrit dans l’ADR pour récupérer abonnement + limites.
     - Décider d’autoriser ou non la session **en fonction de ces données**, pas d’un compteur local isolé.
  3. **Si DC360 ne renvoie que le plan sans compteurs** (cas transitoire) :
     - Implémenter un compteur minimal côté `genesis-ai-service`, mais **prévoyez un champ pour synchronisation future** (ex: appeler un endpoint DC360 pour incrémenter l’usage).  
     - Documenter clairement les hypothèses dans le code + doc.

### 2.3. Comportement attendu côté API

- Si l’utilisateur a encore du quota :
  - L’API doit retourner **200** et exécuter la session (ou l’enfiler).
- Si le quota est dépassé :
  - L’API doit retourner **403** avec un body explicite (code d’erreur type `GENESIS_QUOTA_EXCEEDED`, message clair).
- Important: veiller à ce que le message d’erreur soit suffisamment précis pour le frontend (afin d’éviter les fallbacks silencieux).


---

## 3. Orchestrateur & clés API externes

### 3.1. Clés API (OpenAI, Anthropic, Tavily, LogoAI)

- **Directive**: **ne pas bloquer Sprint 1** en attendant les vraies clés.
- Pour **P0.3 à P0.6**, tu peux avancer avec :
  - **Mocks / fakes** pour les appels externes aux sub-agents.
  - Des implémentations minimales qui retournent des données fictives mais structurées, suffisantes pour :
    - valider le workflow LangGraph,
    - tester la persistance Redis,
    - tester les endpoints API.
- Dès que les clés seront disponibles, on planifiera :
  - une **phase de tests d’intégration ciblés** (hors Sprint 1) pour chaque sub-agent.

### 3.2. Orchestrateur LangGraph

- Pour Sprint 1, l’objectif n’est **pas** d’avoir toute la richesse métier, mais :
  - Un orchestrateur qui :
    - prend un `user_data` ou `BusinessBrief` en entrée,
    - parcourt au moins une partie du workflow (ex: coaching synthétique ou direct),
    - appelle des sub-agents **mockés**,
    - produit un `business_brief` et des `sub_agents_results` structurés,
    - sauvegarde la session dans Redis FS.

---

## 4. Périmètre Sprint 1 – Livrable minimum attendu

### 4.1. Definition of Done Sprint 1

Pour ce premier sprint, le livrable minimum est :

1. **Tests de base stables (P0.3)**
   - `pytest` tourne sans erreurs d’infrastructure (loop/DB/AsyncSession).
   - Les tests rouges restants sont exclusivement liés à des cas métier explicites, si besoin.

2. **Endpoint Business Brief aligné (P0.4)**
   - Endpoint exposé sous un chemin cohérent avec /api/v1/genesis/business-brief/ (ou route documentée clairement si différent).
   - Schémas de requête/réponse alignés avec `API_SCHEMAS_COMPLETS.py`.
   - Cas de test automatisé pour cet endpoint.

3. **Quotas cohérents (P0.5)**
   - Plus de 403 "limite atteinte" renvoyés alors que le front pense que le quota n’est pas épuisé.
   - Comportement bien documenté et testé (au moins tests unitaires sur la couche métier de quotas).

4. **Happy path E2E minimal (P0.6)**
   - Scénario automatisé ou script manuel permettant de vérifier :
     - appel API Business Brief avec données simples,
     - orchestrateur (même partiellement mocké) produit un business brief structuré,
     - session sauvegardée dans Redis FS (présence de fichiers `business_brief.json`, `session_metadata.json`, etc.).

---

## 5. Ressources & coordination

### 5.1. Accès & infos

- **Clés API** :
  - Avance pour l’instant **avec mocks**.
  - Nous ouvrirons un ticket spécifique dès que les clés peuvent être fournies (avec périmètre précis par sub-agent).

- **Payload frontend Genesis** :
  - Se base sur le wizard implémenté dans DigitalCloud360 (`GenesisCoachingPage.jsx`, `AIGenerationStep.jsx`).
  - Le payload Business Brief inclut : `business_name`, `industry_sector`, `vision`, `mission`, `target_market`, `services`, `competitive_advantage`, `years_in_business`, etc.
  - Pour l’alignement, considère ce payload comme **référence pratique**, en le mappant proprement vers les schémas Pydantic.

- **Coordination DC360 quotas/APIs** :
  - Oui, une coordination sera nécessaire.  
  - Pour l’instant, implémente la logique de quotas avec une **API interne claire** (service/fonction dédiée) afin qu’on puisse facilement l’ajuster une fois les décisions business finalisées.

---

## 6. Prochaines actions pour toi

1. **Engager immédiatement P0.3** – corriger les fixtures/tests selon le rapport mi-parcours et valider `pytest` stable.
2. **Passer à P0.4** – aligner le contrat de l’endpoint Business Brief avec `API_SCHEMAS_COMPLETS.py` et le payload front.
3. **Enchaîner avec P0.5** – rendre la logique de quotas cohérente et testée.
4. **Finaliser avec P0.6** – mettre en place un happy path E2E minimal (même avec mocks pour les sub-agents).
5. Documenter les décisions techniques et hypothèses directement dans le repo (`docs/`), en particulier pour :
   - les quotas,
   - les éventuels choix temporaires (mocks, limitations, etc.).

Lorsque ces quatre points seront atteints, nous considérerons le **Sprint 1 réussi** et nous pourrons attaquer l’intégration réelle des sub-agents et des clés API.

---

## 7. Environnement de travail & stack DigitalCloud360

### 7.1. Stacks locales à ta disposition

- **Stack Genesis AI Deep Agents** (backend séparé) :
  - Racine projet : `c:\genesis`
  - Utilisation principale : développement et tests du service `genesis-ai-service` (orchestrateur LangGraph, sub-agents, quotas, tests).

- **Stack DigitalCloud360** (monolithe + frontend React) :
  - Racine projet : `c:\proj`
  - Utilisation principale : tests d’intégration UI ↔ backend via le wizard Genesis dans le dashboard.

Pour le **Sprint 1**, tu peux travailler **uniquement** avec la stack `c:\genesis` pour livrer P0.3 → P0.6. La stack `c:\proj` est désormais opérationnelle et sert surtout à valider les intégrations réelles une fois les endpoints stabilisés.

### 7.2. Démarrage standard des stacks en local

- **DigitalCloud360 (monolithe + frontend + reverse proxy)** :

```bash
cd c:\proj
docker compose up -d db redis web frontend nginx
```

- **Genesis AI service (Deep Agents)** :

```bash
cd c:\genesis
docker compose up -d
```

Avec ces deux commandes, tu obtiens :

- DC360 accessible via `http://localhost` (Nginx → Django API + frontend Vite).
- Genesis AI API accessible via le port défini dans la stack Genesis (cf. docs Genesis pour le mapping exact des ports).

### 7.3. Incident Docker précédent & procédure de résolution

Lors du redémarrage de la stack DigitalCloud360, nous avons rencontré l’erreur suivante :

```bash
docker compose up -d db redis web frontend nginx
Error response from daemon: failed to set up container networking: network <id> not found
```

Symptômes observés :

- Containers `proj-*` en état `Exited (255)`.
- Docker indiquant qu’un réseau interne référencé par les anciens containers n’existait plus.

Procédure de résolution appliquée (sécurisée, les volumes de données sont conservés) :

```bash
cd c:\proj
docker compose down
docker compose up -d db redis web frontend nginx
```

Résultat :

- Réseau `proj_digitalcloud_network` recréé proprement.
- Containers `proj-db-1`, `proj-redis-1`, `proj-web-1`, `digitalcloud360_frontend_dev` en **Healthy**.
- `proj-nginx-1` démarré et exposant `http://localhost`.

**Bon réflexe à retenir** :

- Si, à l’avenir, tu vois un message du type `network <id> not found` lors d’un `docker compose up` pour DC360, tu peux appliquer la même séquence :
  - `docker compose down`
  - puis `docker compose up -d db redis web frontend nginx`
  - en vérifiant ensuite `docker compose ps`.

---
 
**Scrum Master – Genesis AI (Cascade)**
