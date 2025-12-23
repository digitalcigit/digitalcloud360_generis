---
title: "GEN-WO-006: Phase 2 Coaching - Refonte UX Complète"
date: "2025-12-23"
version: "2.0"
sprint: 7
phase: "2"
status: "Validé par PO"
priority: "Haute"
assignee: "Tech Lead Genesis (Senior Developer)"
supersedes: null
tags: ["coaching", "ux", "onboarding", "feedback-visuel", "flow-leger"]
---

# 📋 Work Order GEN-WO-006 v2

## Refonte UX Coaching - Version Finale Validée

**Demandeur :** Product Owner  
**Date :** 23 décembre 2025  
**Priorité :** 🔴 Haute  
**Estimation totale :** 48 heures (~6 jours dev)

---

## 🎯 Vision Produit (Validée par PO)

> **L'objectif final est de produire un site qui atteint les objectifs stratégiques, de communication et commerciaux du client.** 
> 
> Il faut un minimum de contenu réfléchi et poussé pour atteindre cet objectif. Le coaching approfondi reste notre produit de base, mais l'expérience doit être fluide et agréable.

---

## ✅ Décisions Validées par le PO

| Fonctionnalité | Décision |
|----------------|----------|
| Refonte UX Coaching | ✅ **VALIDÉ** |
| Flow conversationnel léger | ✅ **VALIDÉ** |
| Étape 0 Onboarding rapide | ✅ **VALIDÉ** |
| Mode Express (3 min) | ❌ **REJETÉ** - On garde uniquement le mode approfondi |
| Mode Approfondi (15 min) | ✅ **VALIDÉ** - Produit de base |
| Questions approfondissement IA | ✅ **VALIDÉ** - 1-2 max par étape |
| Feedback visuel immédiat | ✅ **VALIDÉ** |
| Aperçu Live du site | ⏸️ **REPORTÉ** - Pas pour V1 |

---

## 📦 Livrables

---

### Chantier 1 : Étape 0 - Onboarding Rapide (Priorité 🔴)
**Effort :** 6h

**Description :** Avant le coaching, poser 3 questions rapides pour personnaliser toute l'expérience.

**Questions Onboarding :**
1. **Nom du projet** → "Comment s'appelle votre entreprise/projet ?" (ou "Je n'ai pas encore de nom")
2. **Secteur d'activité** → Liste déroulante (restaurant, salon, commerce, services, artisanat, etc.)
3. **Logo** → "Avez-vous un logo ?" (Upload / Générer / Plus tard)

**Tâches :**
- [ ] Créer page `/coaching/onboarding` avec les 3 questions
- [ ] Composant `LogoUploader.tsx` (drag & drop)
- [ ] Stocker `business_name`, `sector`, `logo_url` dans session Redis
- [ ] Endpoint POST `/api/v1/coaching/onboarding`
- [ ] Redirection vers `/coaching` après validation

**Fichiers :**
- `genesis-frontend/src/app/coaching/onboarding/page.tsx` (nouveau)
- `genesis-frontend/src/components/LogoUploader.tsx` (nouveau)
- `app/api/v1/coaching.py` (nouvel endpoint)

**Maquette UI :**
```
┌─────────────────────────────────────────────────┐
│  🚀 Bienvenue sur Genesis AI !                  │
│                                                 │
│  Avant de commencer, quelques infos rapides :   │
│                                                 │
│  1. Nom de votre projet                         │
│  ┌─────────────────────────────────────────┐   │
│  │ Mon Super Business                       │   │
│  └─────────────────────────────────────────┘   │
│  □ Je n'ai pas encore de nom                    │
│                                                 │
│  2. Secteur d'activité                          │
│  ┌─────────────────────────────────────────┐   │
│  │ Restaurant / Alimentation           ▼   │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  3. Avez-vous un logo ?                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ 📤 Upload│ │ 🎨 Générer│ │ ⏭️ Plus  │        │
│  │ mon logo │ │ avec IA  │ │   tard   │        │
│  └──────────┘ └──────────┘ └──────────┘        │
│                                                 │
│            [Commencer le coaching →]            │
└─────────────────────────────────────────────────┘
```

---

### Chantier 2 : Flow Conversationnel Léger (Priorité 🔴)
**Effort :** 8h

**Principes validés :**
- **1 seule question à la fois** (pas de mur de texte)
- **Option "Je ne sais pas"** pour skip une question
- **Barre de progression animée** visible en permanence

**Tâches :**
- [ ] Refactoriser l'affichage pour 1 question par écran
- [ ] Ajouter bouton "Je ne sais pas / Passer" sous chaque question
- [ ] Si skip → utiliser valeur par défaut intelligente basée sur secteur
- [ ] Créer composant `ProgressBar.tsx` animé (étape X/5)
- [ ] Animation de transition entre questions (slide ou fade)

**Fichiers :**
- `genesis-frontend/src/app/coaching/page.tsx` (refactorisation)
- `genesis-frontend/src/components/ProgressBar.tsx` (nouveau)
- `genesis-frontend/src/components/SkipButton.tsx` (nouveau)
- `app/api/v1/coaching.py` (gérer skip avec valeurs défaut)

**Comportement "Je ne sais pas" :**
```python
# Si l'utilisateur skip une étape, utiliser valeur par défaut
SKIP_DEFAULTS = {
    "vision": "Créer un business à impact positif pour ma communauté",
    "mission": "Offrir un service de qualité accessible à tous",
    "clientele": "Familles et professionnels de ma région",
    "differenciation": "Un accompagnement personnalisé et authentique",
    "offre": "Des services adaptés aux besoins locaux"
}
```

---

### Chantier 3 : Messages Coaching Épurés (Priorité 🔴)
**Effort :** 6h

**Principe :** Séparer "Prompt IA" (invisible) du "Message Affiché" (épuré, 2-3 lignes max).

**Structure proposée :**
```python
class CoachingStep:
    # Pour l'IA (invisible à l'utilisateur)
    system_prompt: str      # Instructions complètes pour le LLM
    validation_criteria: str # Critères de validation
    
    # Pour l'utilisateur (affiché)
    user_greeting: str      # 1 ligne de salutation
    user_question: str      # 1 question claire
    clickable_choices: list # 3 exemples cliquables
```

**Tâches :**
- [ ] Réécrire les 5 messages utilisateur (courts, chaleureux)
- [ ] Créer fichier `PROMPTS_USER_MESSAGES.py` séparé
- [ ] Modifier API pour retourner uniquement `user_greeting`, `user_question`, `choices`
- [ ] Supprimer affichage des sections techniques

**Exemple Avant/Après :**

AVANT (25 lignes affichées) :
```
ÉTAPE 1/5: COACHING VISION ENTREPRENEURIALE
CONTEXTE UTILISATEUR:
- Profil: Entrepreneur
- Secteur: default
OBJECTIF ÉTAPE: Clarifier rêve transformation...
[... 20 lignes de plus ...]
```

APRÈS (4 lignes affichées) :
```
👁️ Votre Vision

Quel rêve voulez-vous réaliser avec votre business ?

💡 Inspirez-vous :
[Bouton 1] [Bouton 2] [Bouton 3]
```

**Fichiers :**
- `app/services/PROMPTS_USER_MESSAGES.py` (nouveau)
- `app/services/prompts_loader.py` (séparation)
- `app/api/v1/coaching.py` (retour épuré)

---

### Chantier 4 : Questions d'Approfondissement Simplifiées (Priorité 🔴)
**Effort :** 4h

**Décision PO :** Les questions d'approfondissement IA sont utiles mais doivent être :
- **1-2 questions max par étape** (pas de boucle infinie)
- **Simples et directes** (pas de jargon)
- **Optionnelles** (l'utilisateur peut valider sans répondre)

**Tâches :**
- [ ] Modifier logique : max 2 clarifications par étape (déjà 1 via Quick Fix ADR-008)
- [ ] Reformuler les questions de clarification (plus simples)
- [ ] Ajouter bouton "Valider ma réponse" à côté de "Répondre à la question"
- [ ] Si 2 clarifications atteintes → validation automatique

**Fichiers :**
- `app/services/coaching_llm_service.py`
- `app/services/PROMPTS_COACHING_METHODOLOGIE.py`
- `app/api/v1/coaching.py`

**Nouveau flow :**
```
Utilisateur répond → LLM évalue
  ├─ Réponse complète → ✅ Validation directe
  └─ Réponse vague → 1 question simple
       ├─ Utilisateur répond → ✅ Validation
       └─ Utilisateur clique "Valider quand même" → ✅ Validation
```

---

### Chantier 5 : Feedback Visuel Immédiat (Priorité 🟠)
**Effort :** 6h

**Éléments validés :**
- ✨ **Animation de validation** quand réponse acceptée
- 📝 **Résumé 1 ligne** de la réponse reformulée
- ➡️ **Transition animée** vers étape suivante

**Tâches :**
- [ ] Animation confetti/check quand étape validée
- [ ] Afficher résumé reformulé en 1 ligne avant transition
- [ ] Animation slide/fade vers étape suivante
- [ ] Son optionnel de validation (désactivable)

**Fichiers :**
- `genesis-frontend/src/components/ValidationFeedback.tsx` (nouveau)
- `genesis-frontend/src/components/StepSummary.tsx` (nouveau)
- `genesis-frontend/src/hooks/useAnimations.ts` (nouveau)

**Maquette Feedback :**
```
┌─────────────────────────────────────────────────┐
│  ✅ Parfait !                                    │
│                                                 │
│  Votre vision :                                 │
│  "Créer un restaurant qui valorise la cuisine  │
│   traditionnelle sénégalaise"                   │
│                                                 │
│  [━━━━━━━━━━░░░░░░░░░░] Étape 2/5              │
│                                                 │
│            [Continuer →]                        │
└─────────────────────────────────────────────────┘
```

---

### Chantier 6 : Page Résumé CRUD (Priorité 🟠)
**Effort :** 8h

**Tâches :**
- [ ] Créer page `/coaching/summary` après étape 5
- [ ] Afficher résumé des 5 réponses + nom projet + logo
- [ ] Bouton "Modifier" pour chaque section (inline edit)
- [ ] Bouton "Générer mon site" en bas
- [ ] Persister modifications dans Redis

**Fichiers :**
- `genesis-frontend/src/app/coaching/summary/page.tsx` (nouveau)
- `app/api/v1/coaching.py` (endpoint PUT pour update)

---

### Chantier 7 : Persistance PostgreSQL (Priorité 🟠)
**Effort :** 4h

**Tâches :**
- [ ] Créer table `generated_sites` (id, user_id, brief_id, site_definition JSONB, created_at)
- [ ] Migration Alembic
- [ ] Sauvegarder site final en PostgreSQL (permanent)
- [ ] Redis = cache, PostgreSQL = source de vérité

**Fichiers :**
- `app/models/site.py` (nouveau)
- `alembic/versions/xxx_add_generated_sites.py`
- `app/api/v1/sites.py`

---

### Chantier 8 : Thèmes Variés par Secteur (Priorité 🟡)
**Effort :** 6h

**Tâches :**
- [ ] Définir 5 thèmes (Modern, Classic, Bold, Minimal, Warm)
- [ ] Mapping secteur → thème
- [ ] Appliquer dans Transformer

**Fichiers :**
- `app/services/sector_mappings.py`
- `app/services/transformer.py`

---

## 📅 Planning

| Phase | Jours | Chantiers | Effort |
|-------|-------|-----------|--------|
| **A - Critique** | J1-J3 | 1 (Onboarding) + 2 (Flow léger) + 3 (Messages épurés) | 20h |
| **B - Core** | J4-J5 | 4 (Approfondissement) + 5 (Feedback visuel) | 10h |
| **C - Finition** | J6 | 6 (CRUD) + 7 (PostgreSQL) + 8 (Thèmes) | 18h |

**Total :** 48h (~6 jours)

---

## ✅ Critères d'Acceptation

### Phase A - UX Critique
- [ ] Étape 0 collecte nom, secteur, logo (optionnel)
- [ ] 1 seule question affichée à la fois
- [ ] Bouton "Je ne sais pas" fonctionne
- [ ] Barre de progression visible
- [ ] Messages épurés (3-4 lignes max)

### Phase B - Qualité
- [ ] Max 1-2 questions approfondissement par étape
- [ ] Animation validation + résumé 1 ligne
- [ ] Transition fluide entre étapes

### Phase C - Finition
- [ ] Page résumé CRUD fonctionnelle
- [ ] Site persisté en PostgreSQL
- [ ] Thème varie selon secteur

---

## ⏸️ Reporté à V2

- **Aperçu Live du site** pendant le coaching
- **Mode Express** (3 min) - On garde uniquement le mode approfondi
- **Images d'illustration** générées par IA

---

## 📝 Notes Importantes

### Philosophie Produit (PO)
> "L'objectif final est de produire un site qui atteint les objectifs stratégiques, de communication et commerciaux du client. Le coaching approfondi reste notre produit de base."

### Questions d'Approfondissement
> "Le principe des questions d'approfondissement par l'IA n'est pas mal mais nous devons le rendre simple. 1-2 questions pour arriver à un brief de qualité est acceptable."

---

**Créé par :** Cascade (Tech Lead)  
**Validé par :** Product Owner  
**Date validation :** 23 décembre 2025
