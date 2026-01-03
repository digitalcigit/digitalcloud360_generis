# SPÉCIFICATIONS TECHNIQUES DÉTAILLÉES - SELECTION DE THÈME (WO-001)

**Auteur :** Cascade (Tech Lead)
**Destinataire :** Senior Developer
**Date :** 30 Décembre 2025
**Statut :** A VALIDER

---

## 1. VUE D'ENSEMBLE
L'objectif est de briser le monolithe "Coaching -> Site" pour introduire une étape intermédiaire de **Sélection de Thème**.
Nous devons passer d'un mode "Boîte Noire" (l'IA décide de tout) à un mode "Copilote" (l'IA propose, l'utilisateur dispose).

## 2. MODÈLE DE DONNÉES (Back)

### 2.1. Modèle `Theme` (`app/models/theme.py`)
*Déjà initialisé, à vérifier et enrichir si besoin.*
- **Table** : `themes`
- **Champs Clés** :
  - `slug` (Unique): ex: `restaurant-gastronomique-v1`
  - `compatibility_tags`: List[str] (ex: `['food', 'luxury', 'visual']`)
  - `preview_url`: URL vers une démo live (optionnel pour V1, mais prévoir le champ).
  - `config_schema`: JSON (Structure attendue pour la personnalisation du template).

### 2.2. Seeding (`app/scripts/seed_themes.py`)
Créer un script idempotent pour peupler la base avec les 5 thèmes fondateurs :
1. **Nova (Generic)** : Style SaaS/Tech, bleu/blanc, clean.
2. **Savor (Restaurant)** : Focus images, menu intégré, couleurs chaudes.
3. **Luxe (Hotel/Beauty)** : Typo serif, beaucoup d'espace blanc, or/noir.
4. **Impact (NGO/Asso)** : Couleurs terre, focus mission/don.
5. **Craft (Artisan)** : Texture papier, focus portfolio.

## 3. CORE LOGIC (Back)

### 3.1. `ThemeRecommendationAgent` (`app/core/agents/theme_recommender.py`)
Nouvel agent simple (pas de LangGraph complexe nécessaire pour l'instant).
- **LLM** : Deepseek (via `DeepseekProvider`).
- **Prompt Logic** :
  - Input : Business Brief (JSON).
  - Context : Liste des thèmes disponibles (Nom + Description + Tags).
  - Task : "Sélectionne les 3 thèmes les plus pertinents pour ce business."
  - Output format : JSON `[{ "theme_slug": "...", "match_score": 95, "reasoning": "..." }]`.

### 3.2. Refactoring `CoachingLLMService` & `Orchestrator`
- **STOP** : L'orchestrateur actuel (`LangGraphOrchestrator`) lance tout d'un coup.
- **CHANGE** :
  - Créer méthode `finalize_brief(session_id)` qui génère juste le JSON final du brief et le sauvegarde.
  - Ne **PAS** lancer `site_generation` automatiquement.

## 4. API ENDPOINTS (`app/api/v1/`)

### 4.1. Refactor `POST /api/v1/coaching/step`
- Si `current_step` est FINAL (OFFRE terminée) :
  - Générer le Business Brief.
  - Sauvegarder `BusinessBrief` en DB.
  - **Retourner** : `status: "BRIEF_COMPLETED"`, `redirect_to: "/genesis/themes"`.
  - **NE PAS** lancer la génération de site.

### 4.2. New Router `app/api/v1/themes.py`
- `GET /` : Liste tous les thèmes (pour le catalogue).
- `POST /recommend` :
  - Body: `{ session_id: str }`
  - Logic: Appelle `ThemeRecommendationAgent`.
  - Return: Liste des thèmes recommandés.
- `POST /select` :
  - Body: `{ session_id: str, theme_id: str }`
  - Logic:
    1. Met à jour `BusinessContext` avec le thème choisi.
    2. **LANCE** le `LangGraphOrchestrator.run_generation()` (partie génération de site uniquement).
    3. Return: `job_id` ou stream de progression.

## 5. FRONTEND (Next.js)

### 5.1. Page `/genesis/themes`
- **Layout** : "Netflix-style" ou Grid.
- **Top Section** : "Voici 3 recommandations pour [Business Name]".
- **Cards** :
  - Thumbnail du thème.
  - Badge "Recommandé à 95%".
  - Explication IA : "Ce thème met en valeur vos photos de plats..." (tiré du `reasoning`).
- **Interaction** :
  - Click "Preview" -> Modal avec image full screen.
  - Click "Choisir" -> Appel `POST /select` -> Redirection vers Loading Screen.

## 6. INSTRUCTIONS D'IMPLÉMENTATION (Ordre Logique)

1.  **Backend Model & Seed** : Base saine.
2.  **Theme Agent** : Cerveau de la recommandation.
3.  **API Refactor** : Couper le cordon Coaching/Génération.
4.  **Frontend** : UI de sélection.
5.  **Integration** : Rebrancher la génération après la sélection.

---
**Note du Tech Lead :**
*Attention à la gestion des états de session Redis. Assure-toi que `session_id` reste valide entre la fin du chat et la sélection du thème.*
