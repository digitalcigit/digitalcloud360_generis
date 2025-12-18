---
title: "Rapport Final Tests E2E Hub DC360 → Genesis AI"
from: "Tech Lead Genesis AI (Cascade)"
to: "Product Owner DC360 / Genesis, Tech Lead DC360"
date: "29 novembre 2025 - 22h00 UTC"
status: "COMPLETED"
priority: "HIGH"
tags: ["e2e", "sso", "jwt", "docker", "genesis", "dc360"]
reference:
  - "MEMO_RAPPORT_MI_PARCOURS_E2E_29_11_2025.md"
  - "MEMO_SSO_FIX_COMPLET_29_11_2025.md"
  - "MEMO_DIAGNOSTIC_SSO_COOKIE_ABSENT_29_11_2025.md"
---

# 🧪 RAPPORT FINAL – TESTS E2E HUB DC360 → GENESIS AI

## 1. Objet & Contexte

Ce rapport synthétise les tests End-to-End (E2E) réalisés entre le **Hub DigitalCloud360** et **Genesis AI** dans le cadre de la mise en place du **SSO par token JWT via URL**.

**Objectif fonctionnel :**
> Depuis le dashboard Hub, l’utilisateur clique sur **« Lancer Genesis »** et arrive automatiquement connecté sur **Genesis /chat**, sans ressaisir de mot de passe.

**Périmètre testé :**
- Login Hub DC360 (Django + frontend Vite/React)
- Génération / rafraîchissement de tokens JWT (access + refresh)
- Redirection Hub → Genesis avec `?token=<JWT>`
- Validation du token côté Genesis (Next.js 14 / API Routes)
- Création de session Genesis (cookie + contexte React)
- Accès à l’interface de chat `/chat` avec l’email DC360 affiché

---

## 2. Environnement de Test

### 2.1 Infrastructure Docker

- **Réseau partagé :** `dc360-ecosystem-net`
- **Services et ports (host → container)**

| Service              | Host              | Container | URL                         |
|----------------------|-------------------|-----------|-----------------------------|
| Hub Frontend         | `localhost:3000`  | 5173/3000 | `http://localhost:3000`     |
| Hub API (Django)     | `localhost:8000`  | 8000      | `http://localhost:8000`     |
| Genesis Frontend     | `localhost:3002`  | 3000      | `http://localhost:3002`     |
| Genesis API (FastAPI)| `localhost:8002`  | 8000      | `http://localhost:8002`     |

### 2.2 Config réseau Genesis

- `genesis-frontend` et `genesis-api` connectés à :
  - `genesis-ai-network`
  - `dc360-ecosystem-net` (pour joindre le backend Hub DC360 via `http://web:8000`)

- Variables d’environnement clés côté Genesis :
  - `DC360_API_URL=http://web:8000/api`
  - `GENESIS_API_URL=http://genesis-api:8000`

---

## 3. Résumé Exécutif

**Verdict :**

> ✅ Le flux SSO Hub DC360 → Genesis AI est **opérationnel de bout en bout**.  
> ✅ L’utilisateur `dcitest@digital.ci` parvient à accéder à **Genesis /chat** sans ressaisir ses identifiants.

**Points clés observés en DevTools (chrome-devtools) :**

- Hub : présence des cookies `access_token`, `my-app-auth`, `my-refresh-token`.
- Hub : fonction `goToGenesisCoaching` obtient un `accessToken` valide (via cookie ou refresh token).
- Hub : redirection effective vers `http://localhost:3002/?token=<JWT>`.
- Genesis :
  - `GET /?token=...` → 200
  - `POST /api/auth/validate` → 200 (validation auprès du backend DC360 via `http://web:8000/api/auth/user/`)
  - Cookie `access_token` créé côté Genesis
  - URL nettoyée (disparition de `?token=`)
  - Redirection automatique vers `/chat`
- Page `/chat` : affichage de l’email `dcitest@digital.ci` et interface de chat disponible.

---

## 4. Déroulé du Scénario E2E Observé

### 4.1 Étapes côté Hub DC360

1. **Connexion Hub**
   - URL : `http://localhost:3000/login`
   - Identifiants utilisés :
     - Email : `dcitest@digital.ci`
     - Mot de passe : `DiGiT@l2025`
   - Résultat : redirection vers `http://localhost:3000/dashboard`.

2. **État des cookies après login** (extrait) :
   - `access_token=eyJ...` (JWT access token)
   - `my-app-auth=eyJ...` (JWT access token aligné)
   - `my-refresh-token=eyJ...` (refresh token)
   - `csrftoken=...`

3. **Dashboard Hub**
   - Page : `http://localhost:3000/dashboard`
   - Composants visibles :
     - "Bienvenue, **dcitest@digital.ci** !"
     - Bloc "Genesis AI Coach"
     - Bouton **"Lancer Genesis"**

4. **Logique du bouton "Lancer Genesis"** (`DashboardPage.jsx`)

   - Tentative de lecture d’un token existant :
     - `localStorage.getItem('access_token')`
     - `getCookie('my-app-auth')`
   - Si aucun token : utilisation de `my-refresh-token` pour appeler :
     - `POST /api/auth/token/refresh/` → `access` (nouveau access token)
   - Construction de l’URL finale :
     - `http://localhost:3002/?token=<JWT_ACCESS_TOKEN>`
   - Logs console observés :
     - `apiClient: Token refresh successful. Retrying original request.`
     - `SSO: Redirecting to Genesis with token`

### 4.2 Étapes côté Genesis

1. **Arrivée avec Token URL**
   - Requête réseau observée :
     - `GET http://localhost:3002/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` → 200

2. **Traitement dans `AuthContext.tsx`**
   - Extraction du paramètre `token` :
     - `const urlToken = new URLSearchParams(window.location.search).get('token');`
   - Appel à `/api/auth/validate` :
     - `POST /api/auth/validate` avec `{ token: urlToken }` → 200
   - Si succès :
     - Mise à jour de `user` dans le contexte React
     - Création du cookie :
       - `access_token=<JWT>; path=/; max-age=86400; SameSite=Lax`
     - Nettoyage de l’URL :
       - `window.history.replaceState({}, '', '/');`
     - Redirection :
       - `router.push('/chat');`

3. **Validation côté `/api/auth/validate`**
   - Endpoint Next.js : `/api/auth/validate/route.ts`
   - Appelle le backend DC360 via le réseau Docker partagé :
     - `http://web:8000/api/auth/user/` avec header `Authorization: Bearer <token>`
   - Si DC360 répond 200 : renvoie le profil utilisateur à Genesis.

4. **Accès à `/chat`**

   - URL finale observée :
     - `http://localhost:3002/chat` (paramètre `?token=` absent → URL nettoyée)

   - Cookies côté `localhost:3002` :
     - `access_token=...` (Genesis)
     - `my-app-auth=...`
     - `my-refresh-token=...`
     - `csrftoken=...`

   - UI observée :
     - Titre : `Genesis AI`
     - Email affiché : **`dcitest@digital.ci`**
     - Lien : "Retour au Hub" (`http://localhost:3000/`)
     - Zone de chat : `Décrivez votre business...` + bouton "Envoyer"
     - Bloc : "Votre site apparaîtra ici" (intégration future du renderer de site).

---

## 5. Fonctionnalités Implémentées (Résumé Technique)

### 5.1 Hub DC360

- **SSO side – Frontend**
  - Fonction `goToGenesisCoaching` robuste :
    - Lecture d’un `accessToken` existant (localStorage + cookie `my-app-auth`).
    - Fallback via `my-refresh-token` + `POST /api/auth/token/refresh/`.
    - Construction de l’URL SSO : `genesisUrl + '?token=' + accessToken`.

- **Compatibilité avec l’auth réelle Hub**
  - Prise en compte du fait que l’auth Hub est basée sur **session Django + refresh token**, pas seulement un cookie d’access token.

### 5.2 Genesis Frontend

- **AuthContext SSO-aware**
  - Extraction et validation du `token` dans l’URL.
  - Création d’un cookie `access_token` côté Genesis.
  - Nettoyage de l’URL et redirection transparente vers `/chat`.

- **API Next.js**
  - `/api/auth/validate` :
    - Proxy de validation du JWT vers DC360 (`/api/auth/user/`).
  - `/api/auth/me` :
    - Lecture du token présent en cookie (access_token / my-app-auth).
    - Revalidation auprès de DC360 pour récupérer le profil.

- **Intégration UI**
  - Page `/chat` qui affiche l’email de l’utilisateur DC360.
  - Lien de retour vers le Hub.
  - Interface chat prête à dialoguer avec le backend Genesis.

### 5.3 Docker & Réseau

- `genesis-frontend` et `genesis-api` sont tous deux connectés à `dc360-ecosystem-net`.
- Utilisation du hostname `web:8000` côté Genesis pour communiquer avec le backend DC360.

---

## 6. Backlog & Points de Vigilance Restants

Même si le flux SSO principal est fonctionnel, plusieurs chantiers restent recommandés :

### 6.1 Robustesse Auth côté Genesis

- **Expiration de token**
  - Scénario : access token expiré → `/api/auth/me` renvoie 401.
  - Actions à prévoir :
    - Afficher un message clair ("Votre session a expiré, merci de revenir via le Hub DC360").
    - Option avancée : implémenter un mini-flow de refresh côté Genesis si un endpoint adapté côté DC360 est disponible.

- **Gestion des erreurs réseau DC360**
  - Timeouts / 503 sur `http://web:8000/api` doivent être gérés avec une UI explicite.

### 6.2 Sécurité

- Vérifications recommandées :
  - Attributs des cookies (`HttpOnly`, `Secure`, `SameSite`) selon les environnements (dev vs prod HTTPS).
  - Politique d’expiration et de renouvellement pour le cookie `access_token` côté Genesis.

### 6.3 UX & Parcours Utilisateur

- **Déconnexion croisée**
  - Définir le comportement souhaité lorsque l’utilisateur se déconnecte du Hub mais possède encore un cookie actif côté Genesis.
  - Stratégie simple : laisser la session Genesis vivre jusqu’à expiration du JWT.
  - Stratégie avancée : revérifier systématiquement auprès de DC360 sur `/api/auth/me` (déjà en place) et invalider localement dès que DC360 renvoie 401.

- **Messages d’erreur SSO**
  - En cas d’échec de `/api/auth/validate`, proposer une page d’erreur SSO dédiée (plutôt qu’un simple retour silent sur la landing).

### 6.4 Tests & Documentation

- **Tests automatisés**
  - Ajouter des scénarios Playwright/Cypress couvrant :
    - Login Hub → clic "Lancer Genesis" → `/chat` avec email affiché.
    - Token expiré.
    - DC360 indisponible.

- **Documentation**
  - Intégrer le schéma SSO final (voir `MEMO_SSO_FIX_COMPLET_29_11_2025.md`).
  - Rédiger un guide "Comment débugger le SSO en local" (ports, docker-compose, URLs, outils DevTools).

---

## 7. Recommandation Finale (GO / NO-GO)

- **Pour un environnement de démonstration / staging :**
  - **GO** ✅ – Le flux SSO Hub → Genesis est suffisamment robuste et aligné avec les objectifs du PoC.

- **Pour une mise en production :**
  - GO **conditionnel** ⚠️ – Sous réserve de :
    - Durcissement des aspects sécurité (cookies, expiry, logs).
    - Ajout de tests E2E automatisés.
    - Clarification des comportements en cas d’expiration / déconnexion / indisponibilité DC360.

---

## 8. Conclusion

Les travaux réalisés sur le SSO Hub DC360 → Genesis AI permettent désormais :

- Une **expérience utilisateur fluide** (un seul login Hub, accès direct à Genesis /chat).
- Une **séparation claire des responsabilités** :
  - DC360 = source de vérité pour l’authentification.
  - Genesis = consommateur de JWT via un flux SSO maîtrisé.
- Une **base solide** pour renforcer la sécurité, l’observabilité et l’UX dans les itérations à venir.

Ce rapport peut servir de **référence technique** pour toute évolution future du SSO et de l’intégration Hub ↔ Genesis.
