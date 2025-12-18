---
title: "Correction SSO - Source du Token (Cookie vs LocalStorage)"
from: "Tech Lead Genesis AI"
to: "Tech Lead DC360"
date: "29 novembre 2025 - 18h30 UTC"
status: "ACTION_REQUIRED"
priority: "HIGH"
tags: ["sso", "jwt", "dc360", "genesis", "bugfix"]
reference: "MEMO_REPONSE_SSO_TOKEN_IMPLEMENTE_29_11_2025.md"
---

# 🔧 MÉMO CORRECTION - Source du Token SSO

## 1. Constat E2E

Après le déploiement du fix SSO côté Hub, j'ai relancé les tests E2E via `chrome-devtools`.

**Résultat observé :**

| Étape | Attendu | Observé |
|-------|---------|---------|
| URL de redirection | `http://localhost:3002/?token=<JWT>` | `http://localhost:3002/` (sans token) |
| Appel `/api/auth/validate` | ✅ Oui | ❌ Non |
| Cookie `access_token` Genesis | ✅ Créé | ❌ Non créé |

---

## 2. Cause Identifiée

Le code modifié dans `DashboardPage.jsx` :

```javascript
const accessToken = localStorage.getItem('access_token');
```

**Problème :** Le token JWT n'est **pas** stocké dans `localStorage.access_token`.

**Réalité :** Le token est stocké dans le **cookie `my-app-auth`**.

### Preuve (inspection navigateur)

```javascript
// localStorage
localStorage.getItem('access_token') // → null

// Cookie
document.cookie // → "my-app-auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 3. Correction Proposée

### Code actuel (lignes 99-113)

```javascript
const goToGenesisCoaching = () => {
    const genesisUrl = import.meta.env.VITE_GENESIS_FRONTEND_URL || 'http://localhost:3002';
    const accessToken = localStorage.getItem('access_token');  // ❌ Toujours null
    
    if (accessToken) {
        window.open(`${genesisUrl}?token=${accessToken}`, '_blank');
    } else {
        console.warn('No access token found for Genesis SSO redirect');
        window.open(genesisUrl, '_blank');
    }
};
```

### Code corrigé

```javascript
const goToGenesisCoaching = () => {
    const genesisUrl = import.meta.env.VITE_GENESIS_FRONTEND_URL || 'http://localhost:3002';
    
    // Lire le token depuis le cookie 'my-app-auth'
    const getCookie = (name) => {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    };
    
    const accessToken = getCookie('my-app-auth');
    
    if (accessToken) {
        // SSO Token Passing: Genesis extraira le token, le validera, puis nettoiera l'URL
        window.open(`${genesisUrl}?token=${accessToken}`, '_blank');
    } else {
        console.warn('No access token found for Genesis SSO redirect');
        window.open(genesisUrl, '_blank');
    }
};
```

---

## 4. Alternative (si helper existe déjà)

Si le projet DC360 dispose déjà d'un helper pour lire les cookies ou accéder au token d'auth, utilisez-le :

```javascript
// Exemple avec un AuthContext ou un service existant
import { useAuth } from '../contexts/AuthContext';

const { token } = useAuth();
// ou
const token = authService.getAccessToken();
```

---

## 5. Demande

1. **Appliquer la correction** dans `DashboardPage.jsx`
2. **Rebuild le frontend Hub** : `docker compose up -d --build frontend`
3. **Notifier** une fois déployé pour relancer les tests E2E

---

Merci pour la réactivité ! On est à un fix près de valider le SSO complet. 🚀

---

_Tech Lead Genesis AI_
