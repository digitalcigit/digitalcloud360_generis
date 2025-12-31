---
title: "WO-001: Architecture Flux Sélection de Thème"
status: "Ready for Dev"
assignee: "Senior Developer"
reviewer: "Cascade (Tech Lead)"
branch: "feat/theme-selection-flow"
date: "2025-12-30"
priority: "High"
---

# WORK ORDER 001 - Architecture "Brief First, Theme Second"

## 1. Contexte & Objectif
Nous pivotons l'architecture de génération de site. Actuellement, le site est généré automatiquement à la fin du coaching.
**Nouvel Objectif :**
1.  Le coaching aboutit à la sauvegarde d'un **Business Brief** (actif persistant).
2.  Un **Agent de Recommandation** analyse ce brief pour proposer 3-4 thèmes pertinents issus d'une librairie.
3.  L'utilisateur choisit son thème.
4.  La génération du site se lance uniquement après cette sélection.

## 2. Spécifications Techniques

### A. Backend (FastAPI/Django)

#### 1. Modélisation de Données (`app/models/theme.py`)
Créer un modèle `Theme` (SQLAlchemy/Django ORM) :
-   `id` (UUID)
-   `name` (str) : Nom du thème (ex: "Savor", "Corporate Pro").
-   `description` (str).
-   `category` (enum/str) : "restaurant", "real_estate", "generic", etc.
-   `features` (json) : Liste des fonctionnalités clés.
-   `compatibility_tags` (list[str]) : Tags pour le matching (ex: "luxury", "minimalist", "visual-heavy").
-   `thumbnail_url` (str).
-   `is_active` (bool).

**Tâche :** Créer la migration et un script de seed (`app/scripts/seed_themes.py`) avec au moins :
-   2 thèmes "Expert" (ex: Restaurant, Beauté).
-   2 thèmes "Générique" (Business, Startup).

#### 2. Agent de Recommandation (`app/core/agents/theme_recommender.py`)
Créer un agent simple (LangChain/DeepSeek) qui :
-   **Input :** Business Brief (JSON).
-   **Process :** Analyse sémantique du brief vs les `compatibility_tags` des thèmes en base.
-   **Output :** Liste ordonnée de `Theme` avec un `match_score` (0-100) et une `reasoning` (pourquoi ce thème ?).

#### 3. API Endpoints (`app/api/v1/themes.py` & `coaching.py`)
-   **UPDATE** `POST /api/v1/coaching/chat` (ou endpoint de fin de session) :
    -   Ne DOIT PLUS déclencher `orchestrator.run_generation()`.
    -   DOIT sauvegarder le `BusinessBrief` et retourner `brief_id` + `status: "brief_completed"`.
-   **CREATE** `POST /api/v1/themes/recommend` :
    -   Input : `{ brief_id: str }`
    -   Output : `{ themes: [ {id, name, match_score, reasoning, thumbnail...} ] }`
-   **CREATE** `POST /api/v1/site/generate` :
    -   Input : `{ brief_id: str, theme_id: str }`
    -   Trigger : Lance l'orchestrateur de génération (LangGraph) avec le thème sélectionné injecté dans le contexte.

### B. Frontend (Next.js)

#### 1. Page de Sélection (`src/app/genesis/themes/page.tsx`)
-   Accessible via `/genesis/themes?brief_id=XYZ`.
-   Appelle `POST /api/v1/themes/recommend` au chargement.
-   Affiche les cartes de thèmes (Thumbnail, Score de pertinence, Description).
-   Bouton "Choisir ce thème" -> Appelle `POST /api/v1/site/generate`.
-   Loader de génération (existant) -> Redirection vers Preview.

#### 2. Mise à jour du Flux Coaching
-   À la fin du chat, au lieu d'afficher "Génération en cours...", afficher "Analyse terminée. Passons au design."
-   Bouton CTA : "Découvrir mes recommandations" -> Redirige vers `/genesis/themes?brief_id=...`.

## 3. Critères d'Acceptation (Definition of Done)
-   [ ] Le modèle `Theme` existe en base et est peuplé.
-   [ ] Le coaching s'arrête bien à l'étape "Brief Validé" sans générer le site.
-   [ ] L'API de recommandation renvoie des thèmes cohérents avec le secteur du brief.
-   [ ] Le frontend permet de sélectionner un thème.
-   [ ] La génération finale utilise bien le thème choisi (le `ContentAgent` et `TemplateAgent` doivent respecter ce choix).

## 4. Notes pour le Dév
-   Utiliser la branche `feat/theme-selection-flow`.
-   Pour l'instant, le `TemplateAgent` existant générait le thème à la volée. Il faudra le modifier pour qu'il **accepte** un `theme_id` en entrée et applique les styles correspondants plutôt que de les inventer.
