---
title: "Guide Technique : Thème Restaurant 'Savor' (V2)"
tags: ["theme", "restaurant", "savor", "frontend", "backend", "blocks"]
status: "active"
date: "2026-01-02"
author: "Cascade (Tech Lead)"
---

# Guide Technique : Thème Restaurant 'Savor' (V2)

Ce guide détaille l'implémentation technique et la configuration du thème "Savor" (V2), spécifiquement optimisé pour le secteur de la restauration.

## 1. Vue d'ensemble

Le thème **Savor V2** introduit une série de composants React spécialisés ("Blocks") et une logique de transformation backend dédiée pour offrir une expérience utilisateur riche et adaptée aux restaurants (menus, horaires, réservation).

### Fonctionnalités Clés
- **Hero Split** : Mise en avant visuelle avec un layout 50/50 (Texte / Image).
- **Menu Block** : Affichage structuré de la carte (Entrées, Plats, Desserts) avec prix et allergènes.
- **About Enhanced** : Section "À propos" enrichie avec des statistiques clés (Années d'expérience, couverts servis...).
- **Footer Restaurant** : Pied de page étendu incluant horaires d'ouverture, adresse détaillée et inscription newsletter.

---

## 2. Architecture des Composants (Frontend)

Les composants sont situés dans `genesis-frontend/src/components/blocks/`.

### 2.1 HeroBlock (`HeroBlock.tsx`)
- **Variante `split`** : Active le mode 2 colonnes.
- **Props spécifiques** :
  - `variant`: "standard" | "split" | "minimal"
  - `image`: URL de l'image (obligatoire pour le mode split).

### 2.2 MenuBlock (`MenuBlock.tsx`)
- **Nouveau composant**.
- **Structure des données** :
  ```typescript
  interface MenuCategory {
    id: string;
    title: string; // ex: "Entrées"
    items: MenuItem[];
  }
  
  interface MenuItem {
    title: string;
    description?: string;
    price: string;
    dietary?: string[]; // ex: ["Vegetarian", "Gluten Free"]
    isHighlight?: boolean; // Mise en avant visuelle
  }
  ```

### 2.3 AboutBlock (`AboutBlock.tsx`)
- **Variante `enhanced`**.
- **Props spécifiques** :
  - `stats`: Array de `{ value: string, label: string }` (Max 3-4 items).

### 2.4 FooterBlock (`FooterBlock.tsx`)
- **Variante `restaurant`**.
- **Champs additionnels** :
  - `openingHours`: Array de `{ days: string, hours: string }`.
  - `contactInfo`: Objet contenant email, tel, adresse.
  - `newsletter`: Configuration du formulaire d'inscription.

---

## 3. Logique de Transformation (Backend)

Le service `BriefToSiteTransformer` (`app/services/transformer.py`) a été mis à jour pour mapper les données du `BusinessBrief` vers ces nouvelles structures.

### 3.1 Détection du Thème
Le transformer détecte le secteur ou la variante de thème configurée (via `sector_config`).
```python
if sector_config.get("theme_variant") == "restaurant":
    variant = "enhanced" # ou "split", "restaurant" selon le bloc
```

### 3.2 Mapping Automatique
- **Hero** : Utilise `theme_variant="restaurant"` pour forcer le `variant="split"`.
- **Menu** : 
  - Tente de récupérer une structure `menu` explicite depuis `content_generation`.
  - **Fallback** : Convertit la liste des `services` en une catégorie "La Carte" si aucun menu structuré n'est fourni.
- **Footer** : Génère automatiquement les horaires (valeurs par défaut) et les infos de contact si le mode restaurant est actif.

---

## 4. Configuration (Sector Config)

Pour activer ce thème pour un secteur donné, la configuration du secteur (`app/services/sector_mappings.py` ou JSON de config) doit inclure :

```json
{
  "theme_variant": "restaurant",
  "section_order": ["hero", "about", "menu", "features", "contact", "footer"],
  "default_icons": ["utensils", "coffee", "star"]
}
```

## 5. Tests & Validation

### Tests E2E
Les tests Playwright (`e2e/savor-v2.spec.ts`) valident :
1. Le rendu des composants spécifiques (sélecteurs CSS/ID).
2. La présence des données structurées (prix, items du menu).
3. L'intégration globale dans la page de prévisualisation.

### Dépannage Courant
- **Erreur `slice` sur le Menu** : Assurez-vous que `services` est bien une liste et non un dictionnaire dans le transformer (Correctif appliqué en v2.1).
- **Images SVG** : Si vous utilisez des placeholders (ex: placehold.co), assurez-vous que `dangerouslyAllowSVG: true` est activé dans `next.config.ts`.
