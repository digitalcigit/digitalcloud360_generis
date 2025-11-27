---
title: "Work Order - Initialisation Genesis Frontend & Core Architecture"
code: "WO-GENESIS-FRONTEND-INIT-S4-001"
priority: "CRITIQUE"
assignee: "Genesis AI Team (Frontend Division)"
reviewer: "Tech Lead Genesis"
date: "2025-11-27"
sprint: "Sprint 4 - Genesis Satellite Launch"
estimated_effort: "3 days"
tags: ["frontend", "nextjs", "architecture", "initialization"]
status: "ready_for_dev"
---

# 🏗️ WORK ORDER : Initialisation Genesis Frontend

## 1. Contexte & Objectifs
Suite à la validation de l'architecture "Hub & Satellites" et du modèle économique modulaire, nous lançons le développement du **Frontend Autonome Genesis**.
Ce WO couvre la **Phase 1A** : mise en place du socle technique.

**Objectif :** Disposer d'une application Next.js fonctionnelle, connectée au SSO DC360, et prête à recevoir le moteur de rendu de site.

## 2. Spécifications Techniques

### 2.1 Stack Technologique
*   **Framework :** Next.js 14+ (App Router)
*   **Language :** TypeScript
*   **Styling :** Tailwind CSS
*   **Components :** shadcn/ui (Radix UI base)
*   **State Management :** Zustand
*   **API Client :** Axios ou Fetch wrapper (typé)

### 2.2 Structure du Projet (Scaffold)
```
genesis-frontend/
├── src/
│   ├── app/               # App Router
│   │   ├── (auth)/        # Routes protégées
│   │   │   ├── dashboard/
│   │   │   ├── editor/
│   │   ├── (public)/      # Routes publiques
│   │   ├── api/           # BFF (Backend for Frontend)
│   │   │   ├── auth/      # Handlers SSO
│   ├── components/        # UI Kit (shadcn)
│   ├── lib/               # Utils, API client
│   ├── types/             # Types TypeScript partagés
│   └── stores/            # Zustand stores
```

### 2.3 Authentification SSO (DC360 Bridge)
*   Implémenter la réception du token JWT DC360 via URL ou Cookie.
*   Middleware Next.js pour protéger les routes `/dashboard` et `/editor`.
*   Validation du token auprès du Backend Genesis (qui proxy vers DC360 si nécessaire).

### 2.4 Schéma "Site Definition" (Contrat d'Interface)
Définir l'interface TypeScript `SiteDefinition` qui sera le cœur du système.
*   Doit supporter : Métadonnées, Thème (couleurs, fontes), Pages, Sections, Blocs.
*   Fichier cible : `src/types/site-definition.ts`.

### 2.5 Préparation Module Registry (Backend)
*   Créer le modèle SQLAlchemy `UserModule` dans le backend existant (`genesis-ai`).
*   Ajouter l'API endpoint `GET /api/v1/modules/my-modules` pour que le frontend sache quoi afficher.

## 3. Tâches Détaillées

1.  [ ] **Setup Repo :** `npx create-next-app@latest` avec options TypeScript, Tailwind, App Router.
2.  [ ] **UI Kit :** Installation `shadcn/ui` et composants de base (Button, Card, Input, Sidebar).
3.  [ ] **Auth Handshake :** Page de réception SSO (`/auth/callback`) qui stocke le token.
4.  [ ] **Type Definition :** Rédaction du fichier `site-definition.ts` complet.
5.  [ ] **Backend Update :** Migration DB pour ajouter la table `user_modules`.

## 4. Critères d'Acceptation (DoD)

- [ ] Le projet Next.js démarre sans erreur (`npm run dev`).
- [ ] Les composants shadcn sont installés et fonctionnels.
- [ ] Une page protégée redirige vers login si pas de token.
- [ ] Le type `SiteDefinition` est validé et documenté.
- [ ] La table `user_modules` existe en base de données.

## 5. Livrables
*   Code source `genesis-frontend` sur nouvelle branche/repo.
*   PR sur `genesis-ai` (backend) pour les modules.
