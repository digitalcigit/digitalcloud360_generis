---
title: "WO-002: Spécification Design Savor V2 (Restaurant Premium)"
status: "Draft"
assignee: "Senior Developer"
reviewer: "Cascade (Tech Lead)"
date: "2026-01-02"
priority: "High"
---

# WORK ORDER 002 - Savor V2 (Restaurant Premium Design)

## 1. Analyse de l'Existant vs Benchmark
L'analyse des thèmes de référence (Basilico, Luxury) via Playwright a révélé les écarts suivants par rapport à notre version actuelle "plate" :

| Élément | Savor V1 (Actuel) | Benchmark (Cible Savor V2) |
|---------|-------------------|----------------------------|
| **Hero** | Image de fond simple avec overlay. | Sliders, Layouts Split (Texte/Image), Typographie "Serif" élégante, Badges flottants. |
| **Menu/Services** | Grille de cartes simple. | **Navigation par Onglets** (Entrées, Plats, etc.), Layout "Liste à points" avec prix alignés à droite. |
| **Typography** | Duo de polices standard (Inter/Inter). | Trio de polices : Heading (Serif), Body (Sans), **Accent (Script/Handwriting)** pour les sous-titres ("Our Story"). |
| **About** | Texte + 1 Image. | Compositions d'images (Collages), masques créatifs, signature visuelle. |
| **Footer** | Liens simples. | Riche : Horaires d'ouverture, Newsletter, Map intégrée, Feed Instagram. |

## 2. Spécifications Techniques

### A. Mise à jour du Design System (`tailwind.config.ts`)
- Ajout d'une police `font-accent` (ex: *Playfair Display* pour les titres, *Great Vibes* pour les touches manuscrites).
- Extension de la palette de couleurs pour inclure des tons "Or/Doré" ou "Terracotta" spécifiques aux restaurants premium.

### B. Évolution des Composants (Blocks)

#### 1. HeroBlock V2
- **Nouveau Prop :** `variant: 'standard' | 'split' | 'slider'`
- **Feature :** Support de la vidéo en background.
- **UI :** Animation d'apparition des textes (Fade Up).

#### 2. MenuBlock (Nouveau !)
- Remplacement ou évolution du `ServicesBlock`.
- **Feature :** Système d'onglets pour filtrer les items par catégorie (ex: "Entrées", "Plats", "Desserts").
- **UI :** Layout "Ligne de Menu" :
  ```
  Carpaccio de Boeuf ........................... 18€
  Description en italique gris clair
  ```

#### 3. FooterBlock V2
- **Nouveau Prop :** `variant: 'simple' | 'restaurant'`
- **UI Restaurant :** 
  - Col 1: Logo + Short Bio
  - Col 2: Horaires d'ouverture (Tableau structuré)
  - Col 3: Contact + Réservation rapide
  - Col 4: Newsletter

### C. Données & Transformer
- Mettre à jour `BriefToSiteTransformer` pour :
  - Générer des catégories de menu structurées.
  - Injecter les horaires d'ouverture (fictifs ou issus du brief).
  - Sélectionner la police "Accent" dans le thème.

## 3. Plan d'Implémentation
1.  **Design System :** Intégrer les nouvelles polices (via Google Fonts dans `layout.tsx`).
2.  **Composants :** Créer `MenuBlock.tsx` et mettre à jour `HeroBlock.tsx` et `FooterBlock.tsx`.
3.  **Transformer :** Mapper les données du brief vers ces nouvelles structures riches.
4.  **Validation :** Test visuel avec le brief "Pâtisserie Dakar Gold".

---
**Note :** L'objectif est de créer un effet "Wow" immédiat avec des animations subtiles et une typographie hiérarchisée.
