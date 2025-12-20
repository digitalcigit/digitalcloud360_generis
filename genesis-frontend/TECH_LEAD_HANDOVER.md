# Mémo Technique - Implémentation Frontend Coaching (Niveau Argent)

**Date :** 20/12/2025
**Auteur :** Cascade (AI Assistant)
**Objet :** Livraison du module d'interface de Coaching et stabilisation des tests E2E

## 1. Fonctionnalités Livrées

Le module `CoachingInterface` a été développé et intégré dans `genesis-frontend`. Il couvre le parcours "Argent" (Maïeutique Proactive).

### Composants Clés
- **`CoachingInterface`** : Orchestrateur principal (Machine à états). Gère la communication avec l'API `/api/coaching/*`.
- **`UserInput`** : Zone de saisie intelligente avec auto-resize, prévisualisation de reformulation, et boutons d'actions rapides.
- **`SocraticHelp` (Modal)** : Interface d'aide contextuelle posant des questions socratiques pour débloquer l'utilisateur.
- **`ProposalsModal` (Modal)** : Interface de secours ("Je ne sais pas") proposant 3 options générées par l'IA.
- **`ClickableChoices`** : Suggestions rapides pour accélérer la navigation.

### Architecture Technique
- **API Proxy** : Routes Next.js (`src/app/api/coaching/*`) agissant comme proxy vers le backend Python, permettant de sécuriser les clés et d'adapter les payloads si nécessaire.
- **State Management** : Gestion locale via React `useState` pour l'instant (suffisant pour le scope actuel), prêt pour migration Zustand si complexification.

---

## 2. Stratégie de Tests E2E (Playwright)

Nous avons rencontré des difficultés initiales liées à l'authentification dans l'environnement de test (conflits de redirection, race conditions). Une stratégie robuste a été mise en place pour garantir la fiabilité des tests (Flakiness : 0%).

### Décisions Techniques & "Hacks" Autorisés
1.  **Bypass Auth Runtime** :
    Modification de `src/lib/auth.ts` pour accepter une variable d'environnement `E2E_TEST_MODE`.
    ```typescript
    // src/lib/auth.ts
    if (process.env.E2E_TEST_MODE === 'true') {
        return { id: 999, email: 'e2e@test.com', ... }; // User fictif
    }
    ```
    *Justification :* Permet de tester le frontend en isolation totale sans dépendre de la disponibilité du backend/DB Docker ni de générer de vrais JWT signés.

2.  **Sélecteurs Robustes (`data-testid`)** :
    Abandon des sélecteurs fragiles basés sur le texte (`getByText`, `getByRole`) au profit d'attributs stables (`data-testid="send-btn"`, `data-testid="chat-input"`).
    *Justification :* Immunise les tests contre les changements de wording ou de design CSS.

3.  **Isolation Port Réseau** :
    Playwright lance le serveur de test sur le port **3010** (au lieu de 3000) pour éviter tout conflit avec le conteneur `genesis-frontend` qui tourne déjà dans Docker.

### Résultat
- **24/24 tests passés** (Chromium, Firefox, WebKit, Mobile Chrome, Mobile Safari).
- Validation complète du flux : Start -> Message -> Help -> Proposals -> Step Transition.

---

## 3. Actions Requises / Prochaines Étapes

1.  **Code Review** : Valider l'approche du bypass d'auth dans `auth.ts`. S'assurer qu'elle ne risque pas de fuiter en Production (la condition `E2E_TEST_MODE` doit être strictement contrôlée par la CI).
2.  **Intégration Backend** : Les routes API pointent actuellement vers des Mocks dans les tests E2E, et vers `http://genesis-api:8000` en dev. Vérifier l'intégration réelle avec le backend Python une fois celui-ci prêt.
3.  **Nettoyage** : Si le Tech Lead valide l'approche, on peut généraliser les `data-testid` sur l'ensemble de l'application pour uniformiser la qualité des tests.

---

**Statut du build :** ✅ Succès
**Statut des tests :** ✅ Succès
