# MEMO : Résolution SSO Token Passing - Hub DC360 → Genesis AI

**Date :** 29 Novembre 2025  
**Auteur :** Cascade (Principal Architect)  
**Statut :** ✅ RÉSOLU  

---

## Résumé Exécutif

Le flux SSO entre le Hub DC360 et Genesis AI est maintenant **100% opérationnel**. L'utilisateur `dcitest@digital.ci` peut cliquer sur "Lancer Genesis" depuis le dashboard Hub et être automatiquement authentifié sur Genesis, redirigé vers `/chat`.

---

## Diagnostic Initial

### Symptôme
Token JWT non passé dans l'URL lors de la redirection Hub → Genesis.

### Causes Racines Identifiées

| Composant | Problème |
|-----------|----------|
| Hub Frontend | `localStorage.access_token` était `null` |
| Hub Frontend | Cookie `my-app-auth` absent (non créé par le backend) |
| Hub Backend | Login retourne JWT dans response body, pas en cookie |
| Genesis Frontend | AuthContext ne détectait pas le `?token=` URL |
| Genesis Frontend | Endpoint `/api/auth/validate` inexistant |
| Genesis Frontend | Mauvaise URL Docker (`localhost` au lieu de `web`) |

---

## Corrections Appliquées

### 1. Hub DC360 - `DashboardPage.jsx`

**Stratégie :** Utiliser le `my-refresh-token` cookie (toujours disponible) pour obtenir un access token frais via l'endpoint `/api/auth/token/refresh/`.

```javascript
const goToGenesisCoaching = async () => {
    // 1. Tenter localStorage ou cookie my-app-auth
    let accessToken = localStorage.getItem('access_token') || getCookie('my-app-auth');
    
    // 2. Fallback: utiliser refresh token
    if (!accessToken) {
        const refreshToken = getCookie('my-refresh-token');
        if (refreshToken) {
            const response = await fetch('/api/auth/token/refresh/', {
                method: 'POST',
                body: JSON.stringify({ refresh: refreshToken })
            });
            accessToken = (await response.json()).access;
        }
    }
    
    // 3. Redirection avec token
    window.open(`${genesisUrl}?token=${accessToken}`, '_blank');
};
```

### 2. Genesis Frontend - `AuthContext.tsx`

**Ajout :** Détection et traitement du token URL.

```typescript
useEffect(() => {
    const urlToken = new URLSearchParams(window.location.search).get('token');
    
    if (urlToken) {
        // Valider auprès du backend DC360
        const response = await fetch('/api/auth/validate', {
            method: 'POST',
            body: JSON.stringify({ token: urlToken })
        });
        
        if (response.ok) {
            // Créer cookie, nettoyer URL, rediriger
            document.cookie = `access_token=${urlToken}; path=/`;
            window.history.replaceState({}, '', '/');
            router.push('/chat');
        }
    }
}, []);
```

### 3. Genesis Frontend - Nouveau `/api/auth/validate/route.ts`

**Création :** Endpoint de validation du token auprès de DC360.

```typescript
const dc360ApiUrl = 'http://web:8000'; // Nom container Docker
const response = await fetch(`${dc360ApiUrl}/api/auth/user/`, {
    headers: { 'Authorization': `Bearer ${token}` }
});
```

### 4. Genesis Frontend - Fix `/api/auth/me/route.ts`

**Correction :** URL de l'endpoint DC360.

- ❌ Avant : `http://web:8000/api/v1/auth/me/`
- ✅ Après : `http://web:8000/api/auth/user/`

### 5. Genesis - `docker-compose.yml`

**Ajout :** Connexion au réseau partagé.

```yaml
frontend:
  networks:
    - genesis-ai-network
    - dc360-ecosystem-net  # Réseau partagé avec Hub

networks:
  dc360-ecosystem-net:
    external: true
```

---

## Validation E2E

| Étape | Résultat |
|-------|----------|
| Login Hub DC360 | ✅ `dcitest@digital.ci` authentifié |
| Clic "Lancer Genesis" | ✅ Token obtenu via refresh |
| Redirection Genesis | ✅ `?token=eyJ...` dans URL |
| Validation token | ✅ `/api/auth/validate` → 200 |
| Cookie créé | ✅ `access_token` présent |
| URL nettoyée | ✅ `http://localhost:3002/chat` |
| Interface Chat | ✅ Email utilisateur affiché |

---

## Architecture SSO Finale

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FLUX SSO COMPLET                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  HUB DC360 (localhost:3000)           GENESIS (localhost:3002)          │
│  ┌─────────────────────────┐          ┌─────────────────────────┐      │
│  │                         │          │                         │      │
│  │  1. User clique         │          │                         │      │
│  │     "Lancer Genesis"    │          │                         │      │
│  │           │             │          │                         │      │
│  │           ▼             │          │                         │      │
│  │  2. Lire refresh cookie │          │                         │      │
│  │     (my-refresh-token)  │          │                         │      │
│  │           │             │          │                         │      │
│  │           ▼             │          │                         │      │
│  │  3. POST /api/auth/     │          │                         │      │
│  │     token/refresh/      │          │                         │      │
│  │           │             │          │                         │      │
│  │           ▼             │          │                         │      │
│  │  4. Obtenir access_token│          │                         │      │
│  │           │             │          │                         │      │
│  │           └─────────────┼──────────┼─► 5. Redirect avec      │      │
│  │                         │          │      ?token=JWT         │      │
│  │                         │          │           │             │      │
│  │                         │          │           ▼             │      │
│  │                         │          │  6. AuthContext détecte │      │
│  │                         │          │     token URL           │      │
│  │                         │          │           │             │      │
│  │                         │          │           ▼             │      │
│  │                         │  ◄───────┼─ 7. POST /api/auth/     │      │
│  │                         │          │     validate (→ DC360)  │      │
│  │                         │          │           │             │      │
│  │                         │          │           ▼             │      │
│  │                         │          │  8. Créer cookie        │      │
│  │                         │          │     access_token        │      │
│  │                         │          │           │             │      │
│  │                         │          │           ▼             │      │
│  │                         │          │  9. Nettoyer URL        │      │
│  │                         │          │           │             │      │
│  │                         │          │           ▼             │      │
│  │                         │          │  10. Redirect /chat     │      │
│  │                         │          │                         │      │
│  └─────────────────────────┘          └─────────────────────────┘      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Fichiers Modifiés

### Hub DC360 (`c:\proj`)
- `frontend/src/pages/DashboardPage.jsx` - Logique refresh token

### Genesis (`c:\genesis`)
- `genesis-frontend/src/context/AuthContext.tsx` - Détection token URL
- `genesis-frontend/src/app/api/auth/validate/route.ts` - **NOUVEAU**
- `genesis-frontend/src/app/api/auth/me/route.ts` - Fix URL endpoint
- `docker-compose.yml` - Réseau partagé

---

## Prochaines Étapes

1. **Tests de régression** - Vérifier que le login direct sur Genesis fonctionne toujours
2. **Expiration token** - Implémenter le refresh automatique côté Genesis
3. **Sécurité** - Ajouter validation du token expiry avant redirect
4. **Monitoring** - Logger les événements SSO pour audit

---

**Fin du Memo**
