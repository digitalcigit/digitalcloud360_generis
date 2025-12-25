---
title: "ADR-008: Quick Fix Validation Coaching Maïeutique"
tags: ["coaching", "validation", "deepseek", "quick-fix"]
status: "adopté"
date: "2025-12-23"
---

# ADR-008: Quick Fix Validation Coaching Maïeutique

## Contexte

Le système de coaching maïeutique posait des questions d'approfondissement en boucle infinie, empêchant la progression des étapes (Vision → Mission → Clientèle → Différenciation → Offre).

**Symptômes observés :**
- Même en cliquant sur un choix prédéfini proposé par le système, une clarification était demandée
- Problème identique avec Kimi K2 et DeepSeek V3 → **pas un problème de provider LLM**

## Diagnostic

### Bug 1 : Sector Mismatch

**Fichier :** `app/api/v1/coaching.py`

**Problème :** Les choix prédéfinis (`clickable_choices`) étaient générés avec `sector="default"` dans `/start`, mais la comparaison Quick Fix utilisait `detected_sector` (ex: "services") dans `/step`.

```python
# /start (ligne 88)
sector="default"  # Choix générés avec "default"

# /step (ligne 151) - AVANT correction
sector=detected_sector  # Peut être "services" → textes différents !
```

**Solution :** Utiliser `sector="default"` pour la comparaison des choix prédéfinis.

### Bug 2 : Compteur Clarifications Non Persisté

**Problème :** Le compteur `clarification_count` était modifié localement dans `brief_context` mais jamais persisté entre les requêtes HTTP.

**Solution :** Persister le compteur dans `session_data` (Redis) au lieu de `brief_context`.

## Décision

Implémenter un Quick Fix en deux parties :

### 1. Bypass Validation pour Choix Prédéfinis

```python
# Comparer avec sector="default" (même que celui utilisé au démarrage)
step_guidance_default = prompts_loader.get_step_prompt(
    step=session_data["current_step"],
    sector="default"  # FIX: Utiliser "default"
)
predefined_texts = [choice["text"] for choice in step_guidance_default.get("clickable_choices", [])]

if is_predefined_choice:
    extraction_result.is_valid = True
    extraction_result.clarification_needed = False
    extraction_result.confidence_score = 1.0
```

### 2. Limite 1 Clarification Maximum par Étape

```python
# Lire compteur depuis session Redis
clarification_key = f"{session_data['current_step']}_clarification_count"
clarification_count = session_data.get(clarification_key, 0)

if clarification_count >= 1:
    extraction_result.is_valid = True
    extraction_result.clarification_needed = False

# Persister compteur si clarification demandée
if not extraction_result.is_valid:
    session_data[clarification_key] = clarification_count + 1
    await redis_client.set(f"session:{session_data['session_id']}", json.dumps(session_data), ex=7200)
```

## Conséquences

### Positives
- ✅ Choix prédéfinis validés immédiatement (1 clic = passage étape suivante)
- ✅ Maximum 1 clarification par étape pour réponses manuelles
- ✅ Test E2E 5 étapes + génération site validé en ~3 minutes

### Négatives
- ⚠️ Réponses très vagues peuvent passer après 1 clarification (qualité réduite)
- ⚠️ Solution temporaire - refonte validation LLM recommandée pour Phase 2

## Fichiers Modifiés

- `app/api/v1/coaching.py` (lignes 137-188)

## Tests de Validation

```
Test E2E Coaching Maïeutique (23/12/2025)
- Vision → Mission : ✅ 1 clic (choix prédéfini)
- Mission → Clientèle : ✅ 1 clic (choix prédéfini)  
- Clientèle → Différenciation : ✅ 1 clic (choix prédéfini)
- Différenciation → Offre : ✅ 1 clarification + 1 réponse
- Offre → Génération Site : ✅ 1 réponse
- Site Preview : ✅ Affiché correctement
```

## Auteurs

- **Diagnostic & Implémentation :** Cascade (Principal Architect)
- **Validation :** PO Test (E2E)
