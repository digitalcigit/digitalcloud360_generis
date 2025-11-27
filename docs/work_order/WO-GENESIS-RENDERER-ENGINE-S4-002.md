---
title: "Work Order - Moteur de Rendu & Transformer (Phase 1B)"
code: "WO-GENESIS-RENDERER-ENGINE-S4-002"
priority: "HAUTE"
assignee: "Genesis AI Team (Fullstack)"
reviewer: "Tech Lead Genesis"
date: "2025-11-27"
sprint: "Sprint 4 - Genesis Satellite Launch"
estimated_effort: "3 days"
tags: ["frontend", "backend", "renderer", "transformer", "site-definition"]
status: "completed"
completion_date: "2025-11-27"
merge_commit: "e42f8406"
---

# 🎨 WORK ORDER : Moteur de Rendu & Transformer (Phase 1B)

## 1. Contexte & Objectifs
La Phase 1A a mis en place le socle Next.js.
La Phase 1B doit rendre ce socle "intelligent" : il doit être capable de **transformer** un Brief Business en un Site Web structuré et de l'**afficher**.

**Objectif :** Passer de "J'ai une idée" (Brief) à "Voici ton site" (Rendu visuel) de manière automatique.

## 2. Spécifications Techniques

### 2.1 Backend : Le "Transformer Engine"
Nous avons besoin d'un service qui convertit le `BusinessBrief` (sémantique) en `SiteDefinition` (structurel).

*   **Service :** `app/services/transformer.py`
*   **Logique :** Mapping intelligent.
    *   `brief.company_name` -> `site.metadata.title`
    *   `brief.mission` -> `site.pages['home'].sections['hero'].subtitle`
    *   `brief.services` -> `site.pages['home'].sections['features']`
*   **Stockage :** Sauvegarder le résultat JSON dans une nouvelle table `sites`.

### 2.2 Frontend : Le "Block Renderer"
Le frontend ne doit pas hardcoder les pages. Il doit lire le JSON `SiteDefinition` et instancier les composants dynamiquement.

*   **Composant Maître :** `<PageRenderer definition={page} />`
*   **Pattern :** Factory Pattern / Switch Case sur `section.type`.
    *   `type: 'hero'` -> Rend `<HeroBlock />`
    *   `type: 'features'` -> Rend `<FeaturesBlock />`
    *   `type: 'text'` -> Rend `<ContentBlock />`

### 2.3 Composants UI (shadcn/ui)
Créer les blocs atomiques de base dans `src/components/blocks/` :
*   `HeroBlock` (Titre, Sous-titre, Image, CTA)
*   `FeaturesBlock` (Grille de 3 cartes)
*   `FooterBlock` (Copyright, Liens)

## 3. Tâches Détaillées

### Backend (Python)
1.  [ ] **Model :** Créer le modèle SQLAlchemy `Site` (id, user_id, definition: JSON).
2.  [ ] **Service :** Implémenter `BriefToSiteTransformer.transform(brief) -> SiteDefinition`.
3.  [ ] **API :** Endpoint `POST /api/v1/sites/generate` (prend un brief_id, crée un site).
4.  [ ] **API :** Endpoint `GET /api/v1/sites/{id}` (renvoie le SiteDefinition).

### Frontend (Next.js)
5.  [ ] **API Client :** Fonction `getSite(id)` dans `lib/api.ts`.
6.  [ ] **Blocks :** Créer les composants `Hero`, `Features`, `Footer` avec Tailwind.
7.  [ ] **Engine :** Créer le composant `<BlockRenderer />` qui mappe le JSON aux composants.
8.  [ ] **Page :** Route dynamique `/sites/[id]` qui charge et affiche le site.

## 4. Critères d'Acceptation (DoD)

- [ ] Je peux appeler l'API backend avec un Brief ID et obtenir un Site ID.
- [ ] Le JSON `SiteDefinition` généré contient bien les textes du Brief.
- [ ] En allant sur `localhost:3000/sites/[id]`, je vois le site s'afficher visuellement.
- [ ] Le design utilise les couleurs définies dans le Brief (via Tailwind config ou style inline).

## 5. Livrables
*   Code Backend (Transformer + API).
*   Code Frontend (Renderer + Blocks).
*   Une démo vidéo ou screenshot d'un site généré automatiquement.
