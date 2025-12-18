---
title: "Diagnostic SSO - Cookie my-app-auth Absent"
from: "Tech Lead Genesis AI (Cascade)"
to: "Tech Lead DC360"
date: "29 novembre 2025 - 19h00 UTC"
status: "DIAGNOSTIC_COMPLET"
priority: "CRITICAL"
tags: ["sso", "jwt", "cookie", "session", "auth", "diagnostic"]
reference: "MEMO_FIX_COOKIE_DEPLOYE_29_11_2025.md"
---

# 🔍 DIAGNOSTIC APPROFONDI - SSO Token Absent

## 1. Contexte

Suite au déploiement du fix lecture cookie (`my-app-auth` au lieu de `localStorage.access_token`), j'ai relancé les tests E2E complets.

**Résultat :** Le SSO ne fonctionne toujours pas.

---

## 2. Preuves Collectées

### 2.1 Console Hub au moment du clic "Lancer Genesis"

```
[warn] No access token found for Genesis SSO redirect
```

→ Le code DC360 exécute bien le fallback car `getCookie('my-app-auth')` retourne `null`.

### 2.2 État des Cookies sur le Hub (localhost:3000)

```javascript
// Exécuté dans la console du navigateur sur http://localhost:3000/dashboard
document.cookie
// Résultat:
"csrftoken=I0xmqatia0o7RIJ5wIIppAVGYtLnfaff; my-refresh-token=eyJ..."
```

| Cookie | Présent | Lisible JS |
|--------|---------|------------|
| `csrftoken` | ✅ | ✅ |
| `my-refresh-token` | ✅ | ✅ |
| `sessionid` | ✅ | ❌ (HttpOnly) |
| **`my-app-auth`** | **❌ ABSENT** | N/A |

### 2.3 Requête API Hub réussie (preuve d'auth fonctionnelle)

```
GET http://localhost:8000/api/auth/user/ → 200 OK

Cookies envoyés:
- csrftoken=...
- sessionid=7lj1rnm83wjbc2xn5qlo7rjd3f4ifhjx  ← Django Session
- my-refresh-token=...

Réponse:
{"id":7,"email":"dcitest@digital.ci",...}
```

→ L'authentification Hub fonctionne via **session Django** (`sessionid`), pas via JWT `my-app-auth`.

### 2.4 État Redux Persist

```javascript
localStorage.getItem('persist:digitalcloud360-root')
// Résultat:
{
  "auth": {
    "user": null,
    "token": null,
    "refreshToken": null,
    "isAuthenticated": false
  }
}
```

→ Redux ne contient pas le token non plus.

---

## 3. Diagnostic

### Cause Racine

Le Hub DC360 utilise une **authentification par session Django** (`sessionid` cookie HttpOnly), et non pas une authentification JWT via cookie `my-app-auth`.

Le cookie `my-app-auth` n'est **jamais créé** par le flow de login Hub actuel.

### Schéma du Flow Actuel

```
┌─────────────────────────────────────────────────────────────┐
│                      HUB DC360                              │
├─────────────────────────────────────────────────────────────┤
│  Login                                                      │
│    ↓                                                        │
│  Backend Django crée:                                       │
│    • sessionid (HttpOnly) ✅                                │
│    • my-refresh-token ✅                                    │
│    • my-app-auth ❌ (jamais créé)                           │
│    ↓                                                        │
│  Clic "Lancer Genesis"                                      │
│    ↓                                                        │
│  getCookie('my-app-auth') → null                            │
│    ↓                                                        │
│  Fallback: window.open('http://localhost:3002/') sans token │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      GENESIS                                │
├─────────────────────────────────────────────────────────────┤
│  Reçoit URL sans ?token=                                    │
│    ↓                                                        │
│  AuthContext: pas de token URL → skip validation            │
│    ↓                                                        │
│  Appel /api/auth/me → 401 (pas de cookie access_token)      │
│    ↓                                                        │
│  Affiche landing non-authentifiée                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Solutions Proposées

### Option A : Créer le cookie `my-app-auth` au login (Recommandé)

Modifier le flow de login Hub pour créer le cookie `my-app-auth` avec le JWT access token :

```python
# Django backend - login view
response.set_cookie(
    'my-app-auth',
    access_token,
    max_age=3600,
    httponly=False,  # IMPORTANT: doit être lisible par JS
    samesite='Lax',
    secure=False  # True en production HTTPS
)
```

### Option B : Lire depuis Redux/Memory au lieu du cookie

Si le JWT est disponible en mémoire (state React), le lire directement :

```javascript
// DashboardPage.jsx
import { useSelector } from 'react-redux';

const goToGenesisCoaching = () => {
    const genesisUrl = import.meta.env.VITE_GENESIS_FRONTEND_URL || 'http://localhost:3002';
    
    // Option 1: Depuis Redux state
    const accessToken = useSelector(state => state.auth.token);
    
    // Option 2: Depuis un AuthContext
    // const { token } = useAuth();
    
    if (accessToken) {
        window.open(`${genesisUrl}?token=${accessToken}`, '_blank');
    } else {
        console.warn('No access token found for Genesis SSO redirect');
        window.open(genesisUrl, '_blank');
    }
};
```

### Option C : Fetch le token avant redirection

Appeler l'API pour obtenir un token frais avant la redirection :

```javascript
const goToGenesisCoaching = async () => {
    const genesisUrl = import.meta.env.VITE_GENESIS_FRONTEND_URL || 'http://localhost:3002';
    
    try {
        // Fetch a fresh access token from backend
        const response = await fetch('/api/auth/token/', {
            credentials: 'include'  // envoie sessionid
        });
        const { access_token } = await response.json();
        
        if (access_token) {
            window.open(`${genesisUrl}?token=${access_token}`, '_blank');
            return;
        }
    } catch (error) {
        console.error('Failed to get token for Genesis SSO:', error);
    }
    
    window.open(genesisUrl, '_blank');
};
```

---

## 5. Vérification Demandée

Avant d'implémenter, merci de confirmer :

1. **Où est stocké le JWT access token côté Hub ?**
   - Cookie `my-app-auth` ? (actuellement absent)
   - Redux state ? (actuellement `null`)
   - Autre location ?

2. **Le backend Hub peut-il générer un endpoint `/api/auth/token/` ?**
   - Qui retourne le JWT access token à partir de la session active

3. **Quelle option préférez-vous ?**
   - A : Cookie `my-app-auth` créé au login
   - B : Lecture depuis Redux/Context
   - C : Fetch token avant redirection

---

## 6. Résumé

| Composant | État | Blocage |
|-----------|------|---------|
| **Genesis AuthContext** | ✅ Prêt | - |
| **Genesis /api/auth/validate** | ✅ Prêt | - |
| **Genesis /api/auth/me** | ✅ Prêt | - |
| **Hub DC360 - Lecture cookie** | ✅ Code OK | Cookie inexistant |
| **Hub DC360 - Cookie my-app-auth** | ❌ Non créé | **BLOQUANT** |

**Le SSO est bloqué car le cookie `my-app-auth` n'est jamais créé par le Hub.**

---

_En attente de votre retour pour finaliser l'intégration SSO._

---

_Tech Lead Genesis AI (Cascade)_
