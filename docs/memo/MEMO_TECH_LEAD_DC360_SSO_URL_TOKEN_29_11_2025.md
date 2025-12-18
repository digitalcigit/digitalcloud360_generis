---
title: "Alignement SSO Hub → Genesis - Passage du Token en URL"
from: "Tech Lead Genesis AI"
to: "Tech Lead DC360"
date: "29 novembre 2025 - 17h40 UTC"
status: "ACTION_REQUIRED"
priority: "HIGH"
tags: ["sso", "genesis", "dc360", "e2e", "jwt", "redirect"]
reference: "MEMO_RETOUR_INFRA_OK_RELAIS_E2E_29_11_2025.md"
---

# 📩 MÉMO TECHNIQUE - SSO Hub → Genesis (Passage du Token)

## 1. Contexte

Suite à votre mémo `MEMO_RETOUR_INFRA_OK_RELAIS_E2E_29_11_2025.md` :

- ✅ **Infra Hub DC360** : UP et stable (web, frontend, db)
- ✅ **Infra Genesis** : UP et stable (genesis-api, genesis-frontend, db, redis)
- ✅ **Réseau partagé** `dc360-ecosystem-net` : opérationnel
- ✅ Redirection Hub → Genesis fonctionnelle (clic "Lancer Genesis" ouvre `http://localhost:3002/`)

Nous avons ensuite lancé les tests E2E via `chrome-devtools` côté navigateur.

---

## 2. Comportement Observé (E2E Réel)

### 2.1 Côté Hub DC360

- URL : `http://localhost:3000/dashboard`
- Utilisateur connecté : `dcitest@digital.ci`
- Plan : "Genesis AI Basic" visible
- Bouton : **"Lancer Genesis"** présent et cliquable
- Action : clic sur **"Lancer Genesis"**

### 2.2 Côté Genesis

Après clic "Lancer Genesis" :

- Page ouverte : `http://localhost:3002/`
- **Important :** l'URL ne contient **pas** de paramètre `?token=...`
- Contenu affiché : Landing page non authentifiée
  - Message : "Bienvenue sur Genesis"
  - CTA : lien "Se connecter via DC360" (retour Hub)

### 2.3 Requêtes réseau Genesis

- `GET http://localhost:3002/api/auth/me` → **503** (fallback session)
- Aucune requête `POST /api/auth/validate` observée
  - Logique : cette route n'est appelée que si un `token` est détecté dans l'URL (`?token=...`).

### 2.4 Cookies côté navigateur (pour `localhost`)

- Présence de cookies d'auth DC360 (access / refresh) valides sur `localhost` (domain large)
- Mais **Genesis** ne repose pas directement sur ces cookies bruts ; la mécanique prévue est :

```text
Hub DC360 → redirection avec ?token=JWT → Genesis → /api/auth/validate → cookie Genesis
```

À ce stade, l'étape **"redirection avec ?token="** n'a pas encore lieu.

---

## 3. Spécification SSO Convenue côté Genesis

Côté Genesis, la mécanique SSO a été implémentée comme suit :

### 3.1 Frontend (AuthContext)

1. **Extraction du token depuis l'URL** :
   - `const urlParams = new URLSearchParams(window.location.search);`
   - `const urlToken = urlParams.get('token');`

2. **Validation serveur** via `/api/auth/validate` (Next.js API Route) :
   - `POST /api/auth/validate` avec `{ token: urlToken }`
   - La route appelle le Hub DC360 (`DC360_API_URL`) pour valider le JWT et récupérer l'utilisateur.

3. **Création du cookie Genesis** :

```ts
document.cookie = `access_token=${urlToken}; path=/; max-age=86400; SameSite=Lax`;
```

4. **Nettoyage de l'URL** :

```ts
window.history.replaceState({}, '', window.location.pathname + window.location.hash);
```

5. **Redirection** vers `/chat` (si validation OK).

### 3.2 Conditions d'Activation

Cette mécanique **ne s'active que si** :

- L'URL d'arrivée côté Genesis contient `?token=...`

Or, actuellement :

- Le Hub appelle seulement : `http://localhost:3002/`
- Donc : pas de `token` → pas de `/api/auth/validate` → pas de cookie → pas de redirection `/chat`.

---

## 4. Écart Identifié & Proposition

### 4.1 Écart

| Élément | Attendu | Observé |
|---------|---------|---------|
| URL de redirection Hub → Genesis | `http://localhost:3002/?token=<JWT>` | `http://localhost:3002/` |
| Appel `/api/auth/validate` côté Genesis | ✅ Oui (si token URL) | ❌ Non (pas de token) |
| Cookie `access_token` (Genesis) | ✅ Créé après validation | ❌ Non créé |

### 4.2 Proposition Minimaliste (Côté Hub DC360)

**Objectif :** Ne pas toucher au modèle d'auth DC360 existant, seulement **réutiliser** le JWT déjà émis pour construire l'URL de redirection.

#### a) Côté Frontend Hub (pseudocode)

Au lieu de :

```ts
window.location.href = 'http://localhost:3002/';
```

Faire :

```ts
const token = accessTokenFromAuthContextOrStore; // JWT déjà présent côté Hub

if (token) {
  window.location.href = `http://localhost:3002/?token=${token}`;
} else {
  // Optionnel: fallback ou message d'erreur
}
```

#### b) Avantages

- **Aucune modification côté backend DC360** (on réutilise le JWT existant).
- **Genesis** gère : validation, cookie, nettoyage d'URL, redirection.
- Le token n'est visible dans l'URL que quelques millisecondes, puis :
  - supprimé de l'URL (`replaceState`)
  - stocké en cookie côté Genesis.

---

## 5. Sécurité & Bonnes Pratiques

### 5.1 "The Token is the Truth"

- L'identité utilisateur doit rester **dérivée du JWT**, pas d'un `userId` passé en clair.
- Côté Genesis, l'API `/api/v1/chat/` ne fait confiance **qu'au token** (via `get_current_user`).

### 5.2 "Chain of Trust"

- Hub DC360 émet le JWT.
- Genesis reçoit le JWT via l'URL, le valide auprès de DC360, puis crée sa propre session (cookie).
- Aucun champ sensible n'est pris directement depuis le frontend.

### 5.3 "Zero Trust Input"

- Toutes les entrées côté Genesis sont validées (Pydantic/Next API Routes).
- Le token n'est jamais *consommé* sans validation serveur.

---

## 6. Plan de Test E2E après Mise à Jour Hub

Une fois la redirection Hub ajustée :

1. Login Hub (`http://localhost:3000`) avec `dcitest@digital.ci`.
2. Clic "Lancer Genesis".
3. Vérifier côté navigateur :
   - Arrivée initiale sur `http://localhost:3002/?token=...`
   - Appel `POST /api/auth/validate` → **200**
   - Cookie `access_token` créé (SameSite=Lax)
   - URL nettoyée (`/chat` sans `?token=`)
   - Chat Genesis accessible sans re-login.

Nous pouvons ensuite produire un **mémo E2E final** cosigné Genesis + DC360.

---

## 7. Demande

1. **Validation de principe** de cette approche (URL avec `?token=`).
2. **Implémentation côté Hub DC360** de la redirection enrichie :
   - `http://localhost:3002/?token=<JWT>`
3. Notification une fois en place, pour que nous relancions la campagne de tests E2E et formalisions le rapport final.

---

Merci pour votre support continu. Une fois ce dernier point aligné, nous pourrons considérer le flux SSO Hub → Genesis comme totalement validé.


_Tech Lead Genesis AI_
