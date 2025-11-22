---
DE: Scrum Master (Cascade)
À: Tech Lead Genesis AI (agnissaneric)
DATE: 2025-11-21
OBJET: Réponse au mémo mi-parcours Sprint 2 – Providers réels, Redis FS & intégration DC360
PRIORITÉ: HAUTE
---

# MEMO – Directives Scrum Master (Sprint 2, mi-parcours)

## 1. Réception de ton mémo & état du Sprint 2

J’ai bien reçu et lu en détail ton mémo du **21/11/2025**.

Constats principaux :

- **Avancement Sprint 2 ~70%** avec un **niveau de qualité très élevé** (logging, tests, structuration du code).
- **S2.1 – Orchestrateur + sub-agents** : livré avec **17 tests** unitaires couvrant `ResearchSubAgent` et `ContentSubAgent`.
- **S2.2 – Providers réels** :
  - `DeepseekProvider` (LLM principal),
  - `KimiProvider` (search + LLM),
  - `DALLEImageProvider` (logos DALL‑E 3),
  - `ProviderFactory` et `settings.get_provider_api_keys()` mis à jour,
  - tests smoke dédiés pour valider l’intégration réelle.

C’est un **bond de maturité majeur** pour l’architecture multi‑provider de Genesis. Le reste du Sprint 2 doit maintenant consolider :

- la **persistance Redis FS** (S2.3),
- la **validation réelle des providers** via les tests smoke,
- au moins **un test E2E intégration** couvrant le flux complet,
- et la **coordination avec DC360** pour les quotas (S2.4).

---

## 2. Priorisation de fin de Sprint 2 (validation de ta séquence)

Ta proposition de séquence :

1. **S2.3 – Redis FS** (corriger la signature + persistance sessions),  
2. **Tests smoke providers** avec vraies clés API,  
3. **Tests E2E orchestrateur → sub‑agents → Redis FS**,  
4. **S2.4 – Coordination DC360** pour les endpoints quotas,

est **validée telle quelle**.

### 2.1. Pourquoi Redis FS d’abord ?

- Tant que `RedisVirtualFileSystem.write_session()` n’a pas la bonne signature `(user_id, brief_id, data)` et que la persistance n’est pas testée :
  - les sessions restent **volatiles**,
  - on ne peut pas parler de workflow “end‑to‑end” crédible.
- **Directive** :
  - S2.3 est la **prochaine priorité absolue**.
  - Estimation 1–2h pour corriger la signature + ajouter des tests lecture/écriture.

### 2.2. Position des tests smoke & E2E

- **Une fois S2.3 corrigé** :
  - Lancer les **tests smoke providers** avec de vraies API keys (staging) pour sécuriser Deepseek, Kimi, DALL‑E.
  - Ajouter **1–2 tests E2E** qui valident :
    - BusinessBrief → orchestrateur → sub‑agents → Redis FS,
    - y compris au moins un chemin nominal.

- **S2.4 DC360** (endpoints quotas) :
  - reste **important**, mais **dépend fortement de l’équipe DC360** et de leurs propres WOs.
  - Pour le Sprint 2 backend Genesis, nous considérons que le coeur est dans :
    - Redis FS corrigé,
    - providers validés,
    - E2E minimal.

---

## 3. Definition of Done officielle – Sprint 2 (côté Genesis)

Pour considérer **Sprint 2 “Done” côté Genesis AI**, la barre est la suivante :

1. **S2.3 – Redis FS corrigé et testé**
   - Signature `write_session(user_id: str, brief_id: str, data: dict)` alignée avec les appels de l’API.
   - Tests qui valident :
     - écriture d’une session,
     - relecture des fichiers/structures attendues,
     - non‑régression sur les autres usages de Redis FS.

2. **Providers réels validés en smoke**
   - `.env` local (non commité) configuré avec **vraies clés API** pour :
     - Deepseek,
     - Kimi,
     - OpenAI (incluant DALL‑E 3),
     - Tavily (si utilisé dans ce sprint).
   - Exécution de :
     - `pytest tests/test_core/test_providers/test_smoke_providers.py -v`
   - Résultats :
     - au moins un run complet **sans échec bloquant**,
     - problèmes éventuels **documentés** (fichier de résultats ou note dans `docs/memo/`).

3. **Au moins un test E2E orchestrateur → sub‑agents → Redis FS**
   - Un scénario couvrant :
     - réception d’un `BusinessBriefPayload` minimal,
     - exécution de l’orchestrateur (avec les sub‑agents clés),
     - génération d’un briefing structuré,
     - persistance de la session dans Redis FS,
     - vérification qu’on peut relire les données attendues.

4. **S2.4 – Intégration DC360 (vision Sprint 2)**
   - Côté Genesis :
     - `DigitalCloud360APIClient` ou équivalent prêt à consommer les endpoints plan/usage/quota,
     - appels centralisés (pas éparpillés dans le code),
     - **fallback mode documenté** si les endpoints DC360 ne sont pas encore en place.
   - Côté DC360 :
     - l’implémentation réelle des endpoints quotas peut être finalisée dans leurs propres WOs (Sprint 3 si besoin).  
   - **Conclusion** :
     - Pour la **clôture technique de Sprint 2 côté Genesis**, nous n’exigeons pas que DC360 ait déjà livré sa part, mais :
       - le client Genesis doit être prêt,
       - les appels doivent être isolés et désactivables proprement,
       - les hypothèses doivent être **clairement documentées**.

---

## 4. Dépendances DC360 & fallback quotas (réponse S2.4)

### 4.1. Endpoints DC360 manquants

- Tu identifies correctement que :
  - `QuotaManager` appelle des routes DC360 du type :
    - `GET /api/v1/users/{user_id}/subscription`,
    - `POST /api/v1/users/{user_id}/genesis-usage`,
  - ces endpoints ne sont pas encore implémentés côté monolithe.

- **Directive** :
  - Maintenir un **fallback mode explicite** côté Genesis tant que DC360 n’est pas prêt :
    - autoriser la session,
    - loguer un warning structlog clair,
    - éventuellement taguer la session comme "non comptabilisée DC360".
  - Ne pas multiplier les endroits où ces endpoints sont appelés : tout doit passer par **un client dédié** (actuel ou futur `DigitalCloud360APIClient`).

### 4.2. Coordination avec les WOs DC360

- Le travail sur les quotas et l’intégration DC360 sera formalisé côté monolithe via leurs propres WOs backend/frontend.
- De ton côté, il suffit pour Sprint 2 de :
  - rendre le **client Genesis prêt** (contrats clairs, code factorisé),
  - garder le fallback activé et bien logué tant que les endpoints DC360 ne sont pas disponibles.

---

## 5. Clés API, budgets providers & environnement

### 5.1. Qui fournit les clés ? (Q3)

- La fourniture des **clés API réelles** (Deepseek, Kimi, OpenAI, Tavily...) et la gestion des **budgets/quotas** relèvent :
  - du **Produit / Direction** et des **Ops**,
  - **pas** du Tech Lead backend seul.

- Ton travail sur :
  - `.env.example` (URLs d’obtention, champs REQUIS vs OPTIONNEL),
  - `settings.get_provider_api_keys()` (filtrage des placeholders `your-`),
  est **exactement ce qu’on attend** au niveau du service.

### 5.2. Environnements recommandés

- **Staging / test** :
  - Clés avec quotas contrôlés,
  - utilisées pour :
    - tests smoke,
    - tests E2E ciblés.

- **Production** :
  - Clés séparées,
  - stockées hors repo (env vars, secret manager),
  - monitoring des coûts (futur sujet avec Ops).

- **Directive Sprint 2** :
  - Continue à structurer le code pour que :
    - les clés viennent **uniquement** de la config (`settings` / env),
    - aucun secret n’apparaisse dans le code ou la doc versionnée.

---

## 6. Documentation & décisions techniques (LogoAI → DALL‑E 3, providers)

### 6.1. ADR LogoAI → DALL‑E 3

- Tu as pris l’initiative d’abandonner LogoAI au profit de **DALL‑E 3** en t’appuyant sur :
  - la réutilisation de `OPENAI_API_KEY`,
  - une qualité d’image supérieure,
  - moins de dépendances externes.

- **Directive** :
  - Oui, cette décision mérite un **ADR court** dans `docs/` :
    - Contexte : choix initial LogoAI, contraintes.
    - Décision : bascule vers DALL‑E 3.
    - Conséquences : meilleure intégration, simplification des clés.

### 6.2. Documentation providers & workflow tests

- Les éléments suivants doivent être **au minimum** documentés (même brièvement) :
  - comment initialiser `ProviderFactory` avec `settings.get_provider_api_keys()`,
  - comment exécuter les **tests smoke** providers,
  - comment lire/interpréter les résultats (succès, skips, erreurs fréquentes),
  - où se situent les **tests E2E** une fois créés.

- Tu peux soit :
  - enrichir un document existant (guide workflow dev),
  - soit créer une courte note dédiée dans `docs/memo/` ou `docs/`.

---

## 7. Prochaines actions concrètes pour toi

Pour la fin de Sprint 2, voici la **to-do ordonnée** que je valide :

1. **Corriger Redis FS (S2.3)**
   - Mettre à jour la signature `write_session()`.
   - Ajouter des tests lecture/écriture sessions.
   - Vérifier qu’aucun appel existant ne casse.

2. **Configurer un `.env` local avec vraies clés API (staging)**
   - Deepseek, Kimi, OpenAI (incluant DALL‑E 3), Tavily.
   - Ne rien commiter, rester strictement en local / secrets.

3. **Exécuter et valider les tests smoke providers**
   - `pytest tests/test_core/test_providers/test_smoke_providers.py -v`
   - Corriger si nécessaire les petits écarts de formats / timeouts.
   - Documenter le résultat (succès, éventuels points à surveiller).

4. **Ajouter au moins un test E2E complet**
   - BusinessBrief minimal → orchestrateur → sub‑agents → Redis FS.
   - Vérifier persistance et format du résultat.

5. **Documenter le fallback DC360 + dépendances quotas**
   - Clarifier dans le code et/ou une courte note :
     - quels endpoints DC360 sont attendus,
     - comment le système se comporte en leur absence (fallback),
     - ce qui sera activé une fois DC360 prêt.

6. **Si temps disponible** : brouillon d’ADR pour DALL‑E 3
   - Même une première version courte suffira, quitte à la compléter ensuite.

En suivant cet ordre, ton estimation de **3–5h de travail restant** pour amener Sprint 2 à ~90–95% est réaliste.

---

## 8. Coordination inter-équipes & gouvernance (DC360, Produit, Ops)

Pour tenir compte des **travaux parallèles** en cours (équipe Genesis, équipe DC360, Produit, Ops), voici le cadrage que je propose :

- **Responsabilité Genesis (toi & backend IA)**
  - Livrer un service `genesis-ai-service` **cohérent, testé et documenté**.
  - Fournir des **contrats d’API clairs et stables** (BusinessBrief, quotas, intégration DC360).
  - Documenter les **hypothèses temporaires** (fallbacks, endpoints DC360 manquants, limites actuelles des providers).

- **Responsabilité DC360 (backend + frontend)**
  - Implémenter les endpoints nécessaires côté monolithe (plans, usage, quotas) en s’alignant sur les contrats exposés par Genesis et sur leurs propres WOs.
  - Intégrer correctement les endpoints `/api/v1/genesis/...` dans le wizard et dans le contexte d’abonnement.
  - Remonter rapidement les écarts constatés (payload, performance, messages d’erreur) pour ajustement côté Genesis.

- **Responsabilité Produit / Ops**
  - Fournir les **clés API réelles** (Deepseek, Kimi, OpenAI, Tavily, etc.) pour au moins un environnement de **staging** et un environnement **production**.
  - Définir et suivre les **budgets/quotas** des providers (coût par session, enveloppe mensuelle, politique de fallback en cas de dépassement).
  - Valider la **Definition of Done fonctionnelle** (ce qui est suffisant pour un déploiement pilote, ce qui est requis pour un lancement public).

- **Rôle du Scrum Master / Tech Lead transverse (Cascade)**
  - Arbitrer les priorités **entre Genesis et DC360** en fonction du Sprint Goal.
  - S’assurer que les contrats d’API et la DoD sont **partagés et compris** des deux côtés.
  - Servir de point d’escalade lorsque :
    - une dépendance DC360 bloque un élément critique Genesis (ou l’inverse),
    - une contrainte Produit/Ops (budget, sécurité, conformité) nécessite un ajustement technique.

**Rythme de synchronisation recommandé** :

- Un **point court régulier** (asynchrone ou call) entre toi et le Tech Lead DC360 pour :
  - synchroniser sur l’état réel des endpoints quotas,
  - vérifier l’impact des changements de contrat,
  - coordonner la mise en place des tests E2E bout‑en‑bout (DC360 ↔ Genesis).
- Des **demandes explicites** à Produit/Ops (via moi) dès que :
  - tu as besoin de clés supplémentaires ou d’un nouvel environnement,
  - un risque de coût ou de quota provider est identifié.

Ce cadre doit te permettre de **te concentrer sur la qualité technique du service Genesis**, tout en rendant explicites les responsabilités des autres équipes dans la réussite globale de l’intégration.

---

**Scrum Master – Genesis AI (Cascade)**
