---
title: "WO GEN-11 — Page /preview pour affichage site généré"
tags: ["gen-11", "frontend", "preview", "react", "next-js"]
status: "ready"
date: "2025-12-15"
story_points: 5
jira: "GEN-11"
---

# Work Order GEN-11 — Page /preview

**De :** Tech Lead Genesis AI  
**À :** Développeur Frontend  
**Date :** 15/12/2025  
**Sprint :** 5  
**Epic :** GEN-3 (Transformer & Renderer)

---

## 🎯 Objectif

Créer la page de prévisualisation qui affiche le site généré en temps réel, avec toolbar responsive et intégration dans le flux chat.

**Critère d'acceptation principal :**
> Utilisateur clique "Voir mon site" dans le chat → Landing Page complète affichée avec tous les blocks

---

## 📊 État Actuel (Baseline)

### Ce qui existe

| Fichier | Description |
|---------|-------------|
| `src/components/BlockRenderer.tsx` | ✅ Renderer dynamique avec 10 blocks |
| `src/app/sites/[id]/page.tsx` | ✅ Page full-screen qui charge un site |
| `src/app/chat/page.tsx` | ⚠️ Split-view avec `SitePreview` placeholder |

### Ce qui manque

| Fichier | Description |
|---------|-------------|
| `src/app/preview/[siteId]/page.tsx` | Page preview dédiée avec toolbar |
| `src/components/PreviewToolbar.tsx` | Toolbar responsive (mobile/tablet/desktop) |
| `src/components/SiteRenderer.tsx` | Wrapper qui applique le thème et rend toutes les sections |
| `src/components/SiteRendererSkeleton.tsx` | Loading state skeleton |

---

## 📋 Sub-tasks

| # | Sub-task | Estimation | Fichier(s) |
|---|----------|------------|------------|
| 1 | Créer `SiteRenderer.tsx` - wrapper avec thème CSS vars | 1h | `src/components/SiteRenderer.tsx` |
| 2 | Créer `SiteRendererSkeleton.tsx` - skeleton loading | 0.5h | `src/components/SiteRendererSkeleton.tsx` |
| 3 | Créer `PreviewToolbar.tsx` - boutons responsive + zoom | 1.5h | `src/components/PreviewToolbar.tsx` |
| 4 | Créer page `/preview/[siteId]/page.tsx` | 2h | `src/app/preview/[siteId]/page.tsx` |
| 5 | Refactorer `SitePreview` dans `/chat/page.tsx` pour utiliser `SiteRenderer` | 1.5h | `src/app/chat/page.tsx` |
| 6 | Ajouter bouton "Ouvrir en plein écran" → `/preview/[siteId]` | 0.5h | `src/app/chat/page.tsx` |
| 7 | Ajouter appel API `/sites/generate` après brief complété | 1h | `src/components/ChatInterface.tsx` |
| 8 | Tests Jest pour SiteRenderer et PreviewToolbar | 1.5h | `src/tests/components/` |

**Total estimé :** 9.5h (~1.2 jours)

---

## 🔧 Spécifications Techniques

### 1. SiteRenderer.tsx

```typescript
// src/components/SiteRenderer.tsx
interface SiteRendererProps {
  siteDefinition: SiteDefinition;
  className?: string;
}

export default function SiteRenderer({ siteDefinition, className }: SiteRendererProps) {
  const homePage = siteDefinition.pages.find(p => p.slug === '/');
  
  return (
    <div className={className} style={{
      '--color-primary': siteDefinition.theme.colors.primary,
      '--color-secondary': siteDefinition.theme.colors.secondary,
      '--color-background': siteDefinition.theme.colors.background,
      '--color-text': siteDefinition.theme.colors.text,
    } as React.CSSProperties}>
      {homePage?.sections.map((section) => (
        <BlockRenderer key={section.id} section={section} />
      ))}
    </div>
  );
}
```

### 2. PreviewToolbar.tsx

```typescript
// src/components/PreviewToolbar.tsx
type ViewportSize = 'mobile' | 'tablet' | 'desktop';

interface PreviewToolbarProps {
  currentViewport: ViewportSize;
  onViewportChange: (size: ViewportSize) => void;
  siteId: string;
  onFullscreen: () => void;
}

// Boutons: 📱 Mobile (375px) | 📱 Tablet (768px) | 🖥️ Desktop (100%)
// Bouton: ⛶ Plein écran → ouvre /preview/[siteId]
```

### 3. Page /preview/[siteId]

```typescript
// src/app/preview/[siteId]/page.tsx
// - Fetch site via GET /api/v1/sites/{siteId}/preview
// - Affiche SiteRenderer en full-screen
// - Toolbar en haut avec responsive toggles
// - Bouton "Retour au chat"
```

### 4. Intégration ChatInterface

```typescript
// Dans ChatInterface.tsx, après brief généré :
// 1. Appeler POST /api/v1/sites/generate { brief_id }
// 2. Récupérer site_id
// 3. Appeler onBriefGenerated({ siteId, siteDefinition })
```

---

## 🔗 Endpoints Backend (Existants)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/sites/generate` | POST | Transforme brief → SiteDefinition |
| `GET /api/v1/sites/{site_id}` | GET | Récupère SiteDefinition complet |
| `GET /api/v1/sites/{site_id}/preview` | GET | Retourne uniquement site_definition |

---

## 📐 Wireframe Preview Page

```
┌─────────────────────────────────────────────────────────────┐
│  [← Chat]     📱  📱  🖥️     Genesis Preview     [⛶ Full]  │  ← Toolbar
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │                   [HERO BLOCK]                      │   │
│  │                                                     │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                   [ABOUT BLOCK]                     │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                  [SERVICES BLOCK]                   │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                  [CONTACT BLOCK]                    │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                  [FOOTER BLOCK]                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Critères d'Acceptation

- [ ] `/preview/[siteId]` affiche le site complet avec tous les blocks
- [ ] Toolbar permet de basculer entre mobile/tablet/desktop
- [ ] Preview dans `/chat` utilise `SiteRenderer` (plus de placeholder)
- [ ] Bouton "Voir mon site" déclenche la génération du site
- [ ] Bouton "Plein écran" ouvre `/preview/[siteId]`
- [ ] Loading skeleton pendant le fetch
- [ ] Gestion erreurs (site not found, auth required)

---

## 🧪 Validation

### Test Manuel (MCP Chrome DevTools)

```bash
# 1. Naviguer vers http://localhost:3002/chat
# 2. Envoyer un message pour générer un brief
# 3. Cliquer "Voir mon site"
# 4. Vérifier que le preview affiche les blocks
# 5. Tester les toggles responsive
# 6. Cliquer "Plein écran" et vérifier /preview/[siteId]
```

### Tests Jest

```bash
npm test -- --testPathPattern="SiteRenderer|PreviewToolbar"
```

---

## 📎 Dépendances

- **GEN-9** ✅ (Block Renderer) - Complété
- **GEN-10** ✅ (Sites API) - Complété
- **Pas de nouvelles dépendances npm**

---

## 📝 Notes Tech Lead

1. **Réutiliser l'existant** : `/sites/[id]/page.tsx` contient déjà la logique de thème CSS vars. Extraire dans `SiteRenderer.tsx`.

2. **API calls** : Utiliser les fonctions existantes dans `src/utils/api.ts` ou créer `generateSite()` et `getSitePreview()`.

3. **État local vs global** : Le `siteId` peut être passé en query param ou stocké dans un store Zustand. Recommandation : query param pour simplifier.

4. **Responsive iframe** : Pour le mode preview responsive, utiliser un `<div>` avec `width` fixe plutôt qu'un iframe pour éviter les problèmes CORS.

---

*Tech Lead Genesis AI — 15/12/2025*
