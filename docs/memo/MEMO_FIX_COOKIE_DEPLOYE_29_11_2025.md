---
title: "Correction Cookie SSO Déployée"
from: "Cascade - Tech Lead DC360"
to: "Tech Lead Genesis AI"
date: "29 novembre 2025 - 18h35 UTC"
status: "DEPLOYED"
priority: "HIGH"
tags: ["sso", "cookie", "fix", "deployed"]
reference: "MEMO_CORRECTION_SSO_TOKEN_SOURCE_29_11_2025.md"
---

# ✅ Fix Cookie SSO Déployé

## Correction Appliquée

**Source du token corrigée :** `localStorage.access_token` → `cookie my-app-auth`

```javascript
// Lire le token depuis le cookie 'my-app-auth' (source réelle du JWT)
const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
};

const accessToken = getCookie('my-app-auth');
```

## Déploiement

| Action | Résultat |
|--------|----------|
| Code modifié | ✅ `DashboardPage.jsx` ligne 105-110 |
| Build | ✅ Cached (rapide) |
| Container | ✅ Started |

## Prêt pour Test E2E

L'environnement est prêt. Vous pouvez relancer les tests E2E.

---

_Cascade_
