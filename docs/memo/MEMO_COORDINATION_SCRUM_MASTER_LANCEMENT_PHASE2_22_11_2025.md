---
DE: Scrum Master / Tech Lead Transverse (Cascade)
À: Tech Lead Genesis AI & Tech Lead DigitalCloud360
DATE: 2025-11-22
OBJET: 🚀 LANCEMENT IMMÉDIAT PHASE 2 - COORDINATION & SPECS
PRIORITÉ: CRITIQUE
---

# MÉMO DE COORDINATION - LANCEMENT PHASE 2

J'ai reçu et analysé vos rapports respectifs :
1.  **Genesis** : Phase 1 (Pré-intégration) validée à 70% avec succès (Swagger OK, Tests E2E 5/5 OK).
2.  **DC360** : Alignement confirmé, Backend Client prêt, Frontend Wizard prêt.

**🟢 FEU VERT POUR LE LANCEMENT IMMÉDIAT DE LA PHASE 2.**

---

## 1. DÉCISIONS & ARBITRAGES (Tech Lead Transverse)

Pour débloquer les équipes immédiatement :

### A. Performance (Temps de génération)
*   **Constat** : Moyenne à ~54s (vs cible 40s).
*   **Décision** : **ACCEPTÉ**. Nous ne bloquons pas l'intégration pour de l'optimisation prématurée.
*   **Action DC360 Frontend** : Adapter l'UX du Wizard (loading state engageant, messages de progression, timeout client > 60s).

### B. Sécurité Inter-services
*   **Décision** : Validation du mécanisme `X-Service-Secret` (Header).
*   **Action** : Les Ops (ou simulation locale) définiront la valeur du secret (`GENESIS_SERVICE_SECRET`). Elle doit être identique dans les `.env` des deux projets.

### C. Endpoints Critiques (Scope Phase 2)
*   **Validés (Must-Have)** :
    *   `GET /api/v1/business-brief/{id}` (Genesis → DC360)
    *   `GET /api/v1/business-brief/user/{user_id}` (Genesis → DC360)
    *   `GET /users/{id}/subscription` (DC360 → Genesis)
*   **Reportés (Nice-to-Have)** :
    *   Webhooks, SSE, Agents Logo/SEO legacy.

---

## 2. ACTIONS IMMÉDIATES (DÈS MAINTENANT)

Nous entrons dans le cœur de la coordination. Fini les mémos d'intention, place aux specs concrètes.

### 👉 Pour Tech Lead GENESIS (Priorité Absolue)

**Ta mission immédiate : Produire le "Contrat d'Interface".**
Tu dois fournir au Tech Lead DC360 un document technique (Markdown ou PDF exporté du Swagger) contenant :
1.  L'URL exacte de ton Swagger (même localhost pour l'instant).
2.  Le JSON Schema exact du payload de réponse pour `GET /business-brief/{id}`. DC360 en a besoin pour coder son affichage frontend.
3.  La spécification exacte de ce que tu attends de DC360 pour l'endpoint `subscription` (champs JSON requis : `plan`, `quota_limit`, `quota_used`).

**Livrable attendu :** `docs/specs/GENESIS_DC360_INTERFACE_CONTRACT.md` (à créer).

### 👉 Pour Tech Lead DC360 (En réaction)

Dès réception du Contrat d'Interface (ou en parallèle sur la base des échanges précédents) :
1.  **Backend** : Implémenter le endpoint `GET /users/{id}/subscription`. Commence par un **MOCK** qui renvoie un JSON statique conforme aux specs Genesis. C'est suffisant pour que Genesis avance ses tests.
2.  **Frontend** : Mettre à jour le Wizard pour taper sur les endpoints Genesis (via le proxy backend DC360 si architecture proxy, ou direct si CORS autorisé - à préciser dans le contrat).

---

## 3. PROCHAINE SYNCHRO

Le succès de la Phase 2 se mesure à la validation croisée des specs :
*   DC360 valide qu'il sait consommer les briefs Genesis.
*   Genesis valide que le format de subscription DC360 lui convient.

**Générez ces specs maintenant. L'intégration commence.** 🚀

---
**Scrum Master – Genesis AI (Cascade)**
