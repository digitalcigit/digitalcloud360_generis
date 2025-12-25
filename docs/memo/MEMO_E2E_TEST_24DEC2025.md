# MEMO - Test E2E Coaching Flow
**Date:** 24/12/2025 06:47 UTC  
**Statut:** En cours - Bloqué sur authentification

---

## 🎯 Objectif
Tester le processus complet de coaching via Playwright UI :
`Onboarding → 5 étapes coaching → Génération site`

---

## ✅ Complété

1. **Tests Pytest (Backend)** - `test_full_coaching_to_site_generation` PASSÉ
2. **Fix 404 `/api/coaching/onboarding`** - Route API Next.js créée

---

## 🚧 Problème Actuel : Boucle Login Infinie

### Symptôme
Page `/login?callbackUrl=/coaching` tourne en boucle avec spinner "Simulation de l'authentification DC360..."

### Cause Racine
```
c:\genesis\genesis-frontend\src\lib\auth.ts → getCurrentUser()
  ↓
Appelle DC360: http://web:8000/api/v1/auth/me/
  ↓
Container 'web' INACCESSIBLE depuis genesis-frontend
  ↓
Erreur: getaddrinfo ENOTFOUND web
  ↓
Boucle: /coaching → validation échoue → /login → token généré → /coaching → ...
```

### Solution à Appliquer
Modifier `c:\genesis\genesis-frontend\src\lib\auth.ts` ligne 47-50 :

```typescript
} catch (error) {
    console.error('SSO validation error:', error);
    // AJOUTER CE FALLBACK:
    console.log('🔄 Fallback: Validating token via Genesis API...');
    try {
        const genesisApiUrl = process.env.GENESIS_API_URL || 'http://genesis-api:8000';
        const genesisResponse = await fetch(`${genesisApiUrl}/api/v1/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        if (genesisResponse.ok) {
            const user = await genesisResponse.json();
            console.log('✅ Token validated via Genesis API');
            return user;
        }
    } catch (genesisError) {
        console.error('Genesis API validation also failed:', genesisError);
    }
    return null;
}
```

Puis rebuild frontend:
```bash
docker-compose -f c:\genesis\docker-compose.yml up -d --build frontend
```

---

## 📁 Fichiers Créés Cette Session

| Fichier | Description |
|---------|-------------|
| `genesis-frontend/src/app/api/coaching/onboarding/route.ts` | Proxy vers backend |
| `genesis-frontend/src/app/api/auth/dev-token/route.ts` | Génère token dev |
| `app/api/v1/auth.py` | Ajout endpoint `/dev-token` |
| `app/services/coaching_prompts_data.py` | Prompts coaching locaux |

---

## 🔧 Commandes Utiles

```bash
# Générer token de test valide
docker exec genesis-api python -c "from app.core.security import create_access_token; print(create_access_token({'sub': '1', 'user_id': 1}))"

# Logs frontend
docker logs genesis-frontend --tail 30

# Rebuild frontend
docker-compose -f c:\genesis\docker-compose.yml up -d --build frontend
```

---

## 📊 TODO

- [x] Modifier `auth.ts` avec fallback Genesis API ✅
- [x] Modifier `api/auth/me/route.ts` avec fallback Genesis API ✅
- [x] Fix `login/page.tsx` : `data.token` → `data.access_token` ✅
- [x] Rebuild frontend ✅
- [ ] Tester flow complet Playwright : Onboarding → Coaching → Site

---

## ✅ Résolu (24/12/2025 ~07:00 UTC)

**Bug Fix:** Boucle login infinie résolue
- **Cause 1:** `api/auth/me/route.ts` n'avait pas le fallback Genesis API
- **Cause 2:** `login/page.tsx` utilisait `data.token` au lieu de `data.access_token`

**Résultat:** Page `/coaching` accessible avec authentification via Genesis API

---

## ✅ Test E2E Complet RÉUSSI (24/12/2025 ~07:15 UTC)

### Bugs Corrigés Cette Session

| Bug | Fichier | Fix |
|-----|---------|-----|
| Boucle login infinie | `api/auth/me/route.ts` | Ajout fallback Genesis API |
| Token field mismatch | `login/page.tsx` | `data.token` → `data.access_token` |
| CORS 400 sur preview | `.env` | Ajout `localhost:3002` à CORS_ORIGINS |
| Image DALL-E non affichée | `next.config.js` | Supprimé (conflictuel avec .ts) |
| | `next.config.ts` | Ajout remotePatterns DALL-E |

### Flow E2E Validé

```
/coaching → Login auto → 5 étapes → "Voir mon site" → /preview/{sessionId}
```

**Sections du site générées :**
- Hero avec titre et CTA
- À Propos (Mission/Vision)
- Features/Services
- Formulaire Contact
- Footer avec logo

### Prochaines Étapes
- [ ] GEN-WO-006 : Refonte UX Coaching Phase 2
