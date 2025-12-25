---
title: "MEMO: Fix Lien DC360 Hub → /coaching/onboarding Validé"
date: 2025-12-24
from: Cascade (Principal Architect DC360)
to: Tech Lead Genesis AI
priority: ✅ COMPLÉTÉ
type: validation_fix
status: résolu
---

# ✅ MEMO: Fix Lien DC360 Hub → /coaching/onboarding Validé

## 1. Actions Réalisées

### Fichiers Modifiés (DC360 Hub)

1. **`c:\proj\frontend\src\pages\DashboardPage.jsx`** (ligne 100-105)
```javascript
const goToGenesisCoaching = () => {
    // Redirection vers le frontend Genesis autonome (Hub & Satellites)
    // GEN-WO-006: Onboarding obligatoire avant coaching (nom projet, secteur, logo)
    const genesisBaseUrl = import.meta.env.VITE_GENESIS_FRONTEND_URL || 'http://localhost:3002';
    window.open(`${genesisBaseUrl}/coaching/onboarding`, '_blank');
};
```

2. **`c:\proj\frontend\src\App.jsx`** (ligne 71-74)
```jsx
<Route
  path="/genesis-coaching"
  element={<ExternalRedirect to={`${import.meta.env.VITE_GENESIS_FRONTEND_URL || 'http://localhost:3002'}/coaching/onboarding`} />}
/>
```

---

## 2. Test E2E Playwright ✅

### Flux Validé
```
DC360 Login (dcitest@digital.ci) 
    → Dashboard 
    → "Lancer Genesis" 
    → http://localhost:3002/coaching/onboarding ✅
```

### Page Onboarding Affichée
- **Titre**: "Bienvenue sur Genesis AI"
- **Champ**: Nom du projet
- **Dropdown**: Secteur d'activité (10 options)
- **Options Logo**: Upload / Générer / Plus tard
- **Bouton**: "Commencer le coaching →"

---

## 3. Checklist de Validation

- [x] Lien DC360 Hub modifié (`/coaching` → `/coaching/onboarding`)
- [x] Test E2E : DC360 → `/coaching/onboarding` fonctionne
- [x] Page onboarding affiche les 3 champs (nom, secteur, logo)
- [ ] Test flow complet : Onboarding → Coaching 5 étapes → Preview (à valider)
- [ ] Validation PO

---

## 4. Historique des Modifications

| Date | Changement | Work Order |
|------|------------|------------|
| 22/12/2025 | `/chat` → `/coaching` | GEN-WO-002 |
| 24/12/2025 | `/coaching` → `/coaching/onboarding` | GEN-WO-006 Phase A |

---

## 5. Flow Utilisateur Final

```
DC360 Hub (Login)
    ↓
Dashboard → "Lancer Genesis"
    ↓
/coaching/onboarding (Étape 0)
    - Nom du projet
    - Secteur d'activité
    - Logo (Upload/Générer/Plus tard)
    ↓
/coaching (Étapes 1-5)
    - Vision
    - Mission
    - Clientèle
    - Différenciation
    - Offre
    ↓
/preview/{sessionId}
    - Site généré avec nom personnalisé
```

---

**Cascade, Principal Architect DC360**  
*24 Décembre 2025, 08:10 UTC*
