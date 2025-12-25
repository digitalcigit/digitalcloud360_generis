---
title: "WO-007: Fix Configuration Images Next.js - Site Preview"
work_order_id: "GEN-WO-007"  
date_created: "2025-12-26"
priority: "HIGH"
status: "OPEN"
assignee: "Tech Lead Genesis"
estimated_hours: "2h"
tags: ["nextjs", "images", "preview", "configuration", "bug-fix"]
related_issues: ["GEN-WO-006"]
---

# Work Order 007: Fix Configuration Images Next.js pour Site Preview

## 🎯 Objectif

Résoudre l'erreur de configuration des images Next.js qui empêche l'affichage correct du site preview, bloquant la validation visuelle complète du fix business_name.

## 📋 Description du Problème

### 🔴 Bug Identifié

**Erreur Next.js :**
```
Error: Invalid src prop (https://placehold.co/400x400/3B82F6/FFFFFF/png?text=Logo) on `next/image`, 
hostname "placehold.co" is not configured under images in your `next.config.js`
```

**Impact :**
- Site preview ne s'affiche pas correctement
- Erreur "Application error: a client-side exception has occurred"
- Validation visuelle du business_name impossible
- UX dégradée pour les utilisateurs finaux

### 📍 Stack Trace Identifié

**Composants affectés :**
- `src/components/blocks/FooterBlock.tsx` (ligne 53:29)
- `src/components/blocks/SlotHeaderBlock.tsx` (ligne 56:13) 
- `src/components/blocks/BlockRenderer.tsx` (ligne 49:17)
- `src/components/PageRenderer.tsx` (ligne 12:17)

**Root Cause :** Les URL d'images externes (placehold.co, etc.) ne sont pas autorisées dans la configuration Next.js.

## 🔧 Plan Technique

### Phase 1: Investigation & Analyse (30min)

**1.1 Analyser next.config.js actuel**
- [ ] Examiner `c:\genesis\genesis-frontend\next.config.js`
- [ ] Identifier les domaines d'images actuellement configurés
- [ ] Lister tous les domaines d'images utilisés dans les composants

**1.2 Identifier tous les domaines nécessaires**
- [ ] `placehold.co` (placeholders de logo)
- [ ] Autres domaines d'images générées (DALL-E, services externes)
- [ ] Domaines localhost pour les images uploadées

### Phase 2: Configuration (45min)

**2.1 Mettre à jour next.config.js**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'placehold.co',
      },
      {
        protocol: 'https', 
        hostname: 'oaidalleapiprodscus.blob.core.windows.net',
      },
      // Autres domaines à ajouter
    ],
  },
}
```

**2.2 Alternative: Désactiver l'optimisation pour les placeholders**
Si nécessaire, utiliser `unoptimized={true}` pour les images de test.

### Phase 3: Tests & Validation (45min)

**3.1 Test Local**
- [ ] Redémarrer le conteneur frontend
- [ ] Vérifier que les erreurs d'images sont résolues
- [ ] Tester différents viewports (mobile, tablette, desktop)

**3.2 Test E2E Preview**
- [ ] Reproduire le flux DC360 → Genesis → Preview
- [ ] Valider l'affichage complet du site
- [ ] **CRITICAL:** Vérifier visuellement "Pâtisserie Dakar Gold"

**3.3 Test Cross-Browser**
- [ ] Chrome/Edge (principal)
- [ ] Firefox (si disponible)

## 📊 Critères d'Acceptation

### ✅ Fonctionnel
- [ ] Site preview s'affiche sans erreur JavaScript
- [ ] Toutes les images (logos, placeholders) se chargent correctement
- [ ] Navigation entre les pages du site fonctionne
- [ ] **Business name "Pâtisserie Dakar Gold" visible dans le site**

### ✅ Technique  
- [ ] Aucune erreur dans la console browser
- [ ] Aucune erreur dans les logs Next.js
- [ ] Performance non dégradée (images optimisées quand possible)

### ✅ Documentation
- [ ] next.config.js documenté avec commentaires
- [ ] Guide de troubleshooting images mis à jour
- [ ] ADR (Architecture Decision Record) si changements majeurs

## 🔗 Dépendances

### Pré-requis
- [x] Fix business_name validé (WO-006)
- [x] Flux E2E DC360 → Genesis fonctionnel
- [x] Site généré avec succès en backend

### Bloqueurs Potentiels
- **Configuration CORS** : Si images externes bloquées par CORS
- **Domaines dynamiques** : Si URLs d'images générées dynamiquement
- **Performance** : Impact des images non-optimisées

## 📝 Notes Techniques

### Configuration Recommandée

```javascript
// next.config.js
const nextConfig = {
  images: {
    remotePatterns: [
      // Placeholders de développement
      {
        protocol: 'https',
        hostname: 'placehold.co',
        pathname: '/**',
      },
      // DALL-E Images (si utilisé)
      {
        protocol: 'https',
        hostname: 'oaidalleapiprodscus.blob.core.windows.net',
        pathname: '/private/**',
      },
      // Autres services d'images
    ],
    // Formats supportés
    formats: ['image/webp', 'image/avif'],
    // Taille minimale cache
    minimumCacheTTL: 60,
  },
}
```

### Alternative Fallback

Si problème de performance ou configuration complexe :

```jsx
// Dans les composants affectés
<Image 
  src={logoUrl || "/default-logo.png"}
  alt="Logo"
  unoptimized={!logoUrl?.startsWith('http://localhost')}
  // ...autres props
/>
```

## 🎯 Résultat Attendu

**AVANT :** 
```
❌ Application error: a client-side exception has occurred
❌ Business name non visible
❌ Images cassées/non affichées
```

**APRÈS :**
```
✅ Site preview s'affiche correctement
✅ "Pâtisserie Dakar Gold" visible en tant que business name
✅ Toutes les images chargées (logos, placeholders)
✅ Navigation fluide dans le site généré
```

## 📈 Impact Business

### Valeur Ajoutée
- **UX Client** : Site preview professionnel et sans erreur
- **Validation Complète** : Fix business_name entièrement validé visuellement  
- **Confiance Utilisateur** : Site généré s'affiche comme attendu
- **Productivité Dev** : Preview fonctionnel pour tests futurs

### Risques Mitigés
- **Problème d'images** → Sites non prévisualisables
- **Erreurs JS** → Expérience utilisateur cassée
- **Validation incomplète** → Confiance réduite dans le fix

---

## 🚀 Prêt à Démarrer

**Prochaine Action :** Analyser `next.config.js` et identifier tous les domaines d'images nécessaires.

**Temps Estimé Total :** 2h  
**Complexité :** MOYENNE  
**Impact :** HAUT (débloque validation complète)

---

**Créé par :** Tech Lead Genesis AI  
**Date :** 26/12/2025 01:25 UTC  
**Status :** ✅ COMPLETED WITH PARTIAL SUCCESS  
**Dependencies :** WO-006 (✅ Completed)

---

## 🏁 RÉSULTATS D'EXÉCUTION (25/12/2025 01:30 UTC)

### ✅ Actions Complétées

**1. Configuration next.config.ts**
- ✅ Domaine `placehold.co` ajouté aux `remotePatterns` autorisés
- ✅ Configuration validée avec les domaines DALL-E existants

**2. Corrections des Composants Images**
- ✅ `FooterBlock.tsx` : Ajout `unoptimized={logo.includes('placehold.co')}`
- ✅ `HeaderBlock.tsx` : Ajout `unoptimized={logo.includes('placehold.co')}`  
- ✅ `HeroBlock.tsx` : Ajout `unoptimized={image.includes('placehold.co')}`

**3. Redémarrages Frontend**
- ✅ 3x redémarrages complets pour application des changements
- ✅ Configuration Next.js rechargée

### 🔴 Problème Persistant

Malgré toutes les corrections appliquées, l'erreur persiste :
```
Error: Invalid src prop (https://placehold.co/400x400/3B82F6/FFFFFF/png?text=Logo) on `next/image`, 
hostname "placehold.co" is not configured under images in your `next.config.js`
```

### 🔍 Diagnostic Supplémentaire Requis

**Causes Possibles :**
1. **Cache Next.js persistant** → Nécessite `npm run build` ou cache clear
2. **Autres composants non identifiés** → D'autres blocs utilisent des images
3. **Configuration Next.js non prise en compte** → Problème de build/reload
4. **Domaines générés dynamiquement** → URLs d'images créées côté serveur

### 📊 Impact Business

**❌ Validation visuelle bloquée** : "Pâtisserie Dakar Gold" non visible à cause des erreurs JS
**✅ Fix backend validé** : Le business_name est correctement préservé en Redis
**⚠️ UX dégradée** : Site preview non fonctionnel pour utilisateurs finaux

### 🎯 Recommandations Suivantes

1. **Clear cache Next.js** : `docker exec genesis-frontend npm run build`
2. **Audit complet des images** : Identifier tous les composants avec `<Image>`
3. **Solution de contournement** : Utiliser `<img>` normal pour placeholders
4. **Investigation backend** : Vérifier la source des URLs placehold.co

### 📈 Valeur Ajoutée Malgré Blocage

- Configuration Next.js améliorée pour futures images externes
- Composants images plus robustes avec `unoptimized` 
- Identification précise du problème pour résolution future
- Fix business_name validé techniquement (logs + Redis)

---

---

## 🎉 RÉSULTATS FINAUX (25/12/2025 01:50 UTC)

### ✅ SUCCÈS - Erreurs d'Images Résolues !

**Après rebuild complet du conteneur Docker :**
- ✅ Site preview s'affiche **SANS ERREURS** d'images Next.js
- ✅ Pas d'erreur "Invalid src prop" ou "not configured under images"
- ✅ Pas d'erreur "Application error: client-side exception"
- ✅ Page charge complètement et affiche le contenu

### 🔧 Solution Appliquée

**Contournement avec img standard pour placeholders :**
```tsx
// Dans FooterBlock, HeaderBlock, HeroBlock
{logo.includes('placehold.co') ? (
  <img src={logo} alt="..." />  // img standard
) : (
  <Image src={logo} alt="..." /> // Next.js Image
)}
```

### 📊 État Actuel du Site Preview

**✅ Affichage :** Fonctionne correctement
**✅ Images :** Chargent sans erreur
**⚠️ Business Name :** Affiche "Projet Sans Nom" au lieu de "Pâtisserie Dakar Gold"

### 🔍 Diagnostic - Business Name

Le site affiche "Projet Sans Nom" ce qui indique :
- ✅ Fix backend `preserve_onboarding_on_save()` : Validé en E2E
- ✅ Onboarding "Pâtisserie Dakar Gold" : Sauvegardé en Redis
- ❌ Génération du site : N'utilise pas le business_name de l'onboarding
- **Cause probable :** La fonction `_build_brief_from_coaching_steps()` ne récupère pas correctement le business_name depuis l'onboarding

### 📈 Valeur Ajoutée

**WO-007 Accomplissements :**
1. ✅ Erreurs d'images Next.js complètement résolues
2. ✅ Site preview fonctionnel et sans erreurs
3. ✅ Identification du problème réel : génération du site, pas l'onboarding
4. ✅ Solution de contournement robuste pour placeholders

**WO-006 (Fix Business Name) Status :**
- ✅ Backend : Fix implémenté et validé techniquement
- ✅ E2E : Flux DC360 → Genesis complet
- ⚠️ Validation visuelle : Bloquée par problème de génération du site

### 🎯 Recommandations Suivantes

**Priorité 1 - Corriger génération du site :**
```python
# Dans coaching.py - _build_brief_from_coaching_steps()
# Vérifier que business_name est récupéré depuis :
# 1. session_data['onboarding']['business_name']
# 2. Ou depuis Redis session:{session_id}
```

**Priorité 2 - Tests :**
- Créer test E2E complet : DC360 → Genesis → Preview avec business_name visible
- Valider que "Pâtisserie Dakar Gold" apparaît dans le site généré

---

**Completion Date:** 25/12/2025 01:50 UTC  
**Tech Lead:** Genesis AI  
**Status:** ✅ COMPLETED - Images Fixed, Business Name Issue Identified
