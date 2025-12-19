---
title: "Work Order GEN-16 — Intégration Chat ↔ pgvector Memory"
date: "2025-12-19"
sprint: 6
phase: "2"
status: "En Cours"
priority: "🔴 Haute"
effort: "3 points"
tags: ["genesis", "phase2", "pgvector", "chat", "memory", "embeddings"]
---

# 📋 Work Order GEN-16 — Chat ↔ pgvector Memory

## 🎯 Objectif

> **Connecter le système de mémoire sémantique pgvector au chat** pour enrichir l'expérience utilisateur avec des recommandations basées sur les briefs similaires.

---

## 📊 Contexte

### Infrastructure Existante
- ✅ **GEN-13** : LangGraph Orchestrator connecté au chat
- ✅ **GEN-15** : pgvector installé avec table `user_embeddings`
- ✅ **API** : Endpoints `/memory/similar` et `/memory/user` fonctionnels
- ✅ **VectorStore** : Service d'embedding OpenAI opérationnel

### Problème Actuel
Les briefs générés ne sont **pas stockés** dans la mémoire sémantique. Le système pgvector est installé mais non utilisé par le chat.

---

## 🔧 Tâches

### 1. Stocker les Embeddings après Génération de Brief

**Fichier :** `app/api/v1/chat.py`

**Action :** Après génération réussie d'un brief, créer un embedding et le stocker.

```python
# Après la génération du brief (ligne ~130)
if brief_generated and site_data:
    # Stocker l'embedding pour recommandations futures
    try:
        text_to_embed = f"{business_context.get('business_name', '')} - {business_context.get('sector', '')} - {business_context.get('description', '')}"
        await vector_store.store_embedding(
            db=db,
            user_id=current_user.id,
            brief_id=brief_id,
            text=text_to_embed,
            embedding_type="brief",
            metadata={"sector": business_context.get("sector")}
        )
    except Exception as e:
        logger.warning(f"Failed to store embedding: {e}")
        # Non-bloquant - le brief est généré même si l'embedding échoue
```

### 2. Suggérer des Templates Similaires (Optionnel)

**Fichier :** `app/api/v1/chat.py`

**Action :** Avant génération, chercher des briefs similaires pour suggérer des templates.

```python
# Avant la génération (après extraction du contexte business)
similar_briefs = await vector_store.search_similar(
    db=db,
    query_text=f"{business_context.get('sector', '')} {business_context.get('description', '')}",
    user_id=None,  # Recherche cross-users pour recommandations
    limit=3,
    threshold=0.75
)

if similar_briefs:
    # Ajouter des suggestions au contexte
    suggestions = [brief["metadata"].get("template") for brief in similar_briefs if brief.get("metadata")]
```

### 3. Ajouter l'Import du VectorStore

**Fichier :** `app/api/v1/chat.py`

```python
from app.core.memory.vector_store import VectorStore

# Initialiser le VectorStore
vector_store = VectorStore()
```

---

## 📁 Fichiers à Modifier

| Fichier | Action |
|---------|--------|
| `app/api/v1/chat.py` | Ajouter stockage embeddings après génération |
| `app/core/memory/vector_store.py` | Aucune modification requise |

---

## ✅ Critères d'Acceptation

- [ ] Après génération d'un brief, un embedding est stocké dans `user_embeddings`
- [ ] L'échec du stockage d'embedding ne bloque pas la génération du brief
- [ ] Les embeddings contiennent les métadonnées (sector, template utilisé)
- [ ] (Optionnel) Le chat suggère des templates basés sur les briefs similaires

---

## 🧪 Tests

### Test Manuel
1. Générer un brief via le chat
2. Vérifier dans la DB : `SELECT * FROM user_embeddings ORDER BY created_at DESC LIMIT 1;`
3. Générer un second brief similaire
4. Vérifier que la recherche de similarité retourne le premier brief

### Test Automatisé
```python
# tests/test_api/test_chat_memory.py
async def test_chat_stores_embedding_on_brief_generation():
    # 1. Envoyer un message qui déclenche la génération
    # 2. Vérifier que l'embedding est créé
    # 3. Vérifier les métadonnées
```

---

## 📅 Planning

| Étape | Durée Estimée |
|-------|---------------|
| Import et initialisation VectorStore | 15 min |
| Stockage embedding post-génération | 30 min |
| Tests manuels | 15 min |
| (Optionnel) Suggestions templates | 45 min |

**Total :** ~1h (sans optionnel) / ~2h (avec optionnel)

---

## 🚀 Démarrage

```bash
# Fichier principal à modifier
code c:\genesis\app\api\v1\chat.py

# Vérifier les embeddings stockés
docker exec postgres psql -U genesis_user -d genesis_db -c "SELECT id, user_id, brief_id, embedding_type, created_at FROM user_embeddings ORDER BY created_at DESC LIMIT 5;"
```

---

*Tech Lead Genesis AI*  
*19 décembre 2025*
