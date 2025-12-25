---
title: "Demande d'investigation SSO DC360 → Genesis"
date: "2025-12-21"
status: "pending"
tags: ["dc360", "sso", "auth", "genesis", "logs", "diagnostic"]
---

# Contexte

En test local (navigateur contrôlé), le login DC360 avec `dcitest@digital.ci / DiGiT@l2025` retourne `401 - "Given token not valid for any token type"` sur `POST /api/token/`, ce qui empêche l’émission du jeton et la redirection SSO vers Genesis. Sur d’autres navigateurs, le login fonctionne selon l’utilisateur.

# Objectif

Confirmer le flux SSO complet et collecter les données côté backend DC360 (et front DC360 si utile) pour comprendre pourquoi cette session spécifique est rejetée.

# Périmètre de test à exécuter (par l’architecte DC360)

1) **Login DC360 (port 3000)**
   - Navigateur propre (profil vierge/guest).
   - URL: `http://localhost:3000/login`
   - Credentials: `dcitest@digital.ci / DiGiT@l2025`
   - Observer la requête `POST /api/token/` : statut HTTP, payload envoyé, headers, cookies.

2) **Redirection SSO vers Genesis (port 3002)**
   - Après login, vérifier la présence du paramètre `token` dans l’URL de redirection.
   - Vérifier que le cookie `access_token` est posé côté Genesis.
   - Appel `GET /api/auth/me` (frontend Genesis) ne doit plus renvoyer 503.

3) **Configuration d’API côté Genesis (host vs docker)**
   - Valeur attendue (dev host) : `DC360_API_URL=http://localhost:8000/api`.
   - Vérifier que Genesis appelle bien cette URL (et non `http://web:8000/api`).

# Données/logs attendus

- **Backend DC360** (service web) :
  - Logs autour du `POST /api/token/` avec ces credentials (timestamp, message d’erreur précis DRF/JWT).
  - Confirmation de l’endpoint utilisé (ex: `/api/token/` ou `/api/auth/token/`).
  - Si CSRF/headers spécifiques sont requis, le préciser.

- **Frontend DC360** :
  - Payload exact envoyé sur `/api/token/` (champs user/pass, en-têtes).
  - Eventuels cookies/headers manquants dans la session qui échoue.

- **Frontend Genesis** :
  - Résultat de `GET /api/auth/me` après redirection (statut, message).
  - Si 503, stack trace/log côté Next API route (`src/app/api/auth/me/route.ts`).

# Résultat attendu

- Identifier la cause du 401 dans notre session (différence de payload, endpoint, header, cookie, CSRF ou comptes) et partager les logs détaillés.
- Confirmer le flux complet : login DC360 → token OK → redirection SSO → `access_token` posé → `/api/auth/me` OK → coaching/preview Genesis utilisables.

# Notes complémentaires

- Genesis a été ajusté pour utiliser par défaut `http://localhost:8000/api` en dev host (au lieu de `http://web:8000/api`).
- E2E_TEST_MODE côté Genesis bypass l’auth interne, mais le SSO doit fonctionner en mode normal.
