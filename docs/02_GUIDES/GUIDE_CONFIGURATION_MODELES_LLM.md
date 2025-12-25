---
title: Guide de Configuration des Modèles LLM
date: 2025-12-22
tags: ["configuration", "llm", "providers", "models"]
status: actif
---

# Guide de Configuration des Modèles LLM

## Vue d'ensemble

Genesis AI supporte maintenant une configuration flexible des modèles LLM via variables d'environnement, permettant de changer facilement de modèle sans modifier le code Python.

---

## Configuration Requise (`.env`)

### 1. Clés API (OBLIGATOIRE)

```bash
# Kimi/Moonshot AI (provider actuel pour BASIC)
KIMI_API_KEY=sk-votre_cle_kimi_ici
KIMI_BASE_URL=https://api.moonshot.ai

# DeepSeek (fallback)
DEEPSEEK_API_KEY=sk-votre_cle_deepseek_ici
DEEPSEEK_BASE_URL=https://api.deepseek.com

# OpenAI (plan PRO)
OPENAI_API_KEY=sk-votre_cle_openai_ici

# Anthropic (plan ENTERPRISE)
ANTHROPIC_API_KEY=sk-ant-votre_cle_anthropic_ici
```

**Où obtenir les clés :**
- Kimi : https://platform.moonshot.cn/console/api-keys
- DeepSeek : https://platform.deepseek.com/api_keys
- OpenAI : https://platform.openai.com/api-keys
- Anthropic : https://console.anthropic.com/settings/keys

---

## Configuration des Modèles par Défaut

### Modèles par Provider (dans `.env`)

```bash
# Modèles par défaut pour chaque provider
DEEPSEEK_MODEL=deepseek-chat
KIMI_MODEL=moonshot-v1-128k
OPENAI_MODEL=gpt-4o
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### Overrides par Plan (OPTIONNEL)

Pour forcer un modèle spécifique pour un plan, ajoutez dans `.env` :

```bash
# Override modèle pour plan BASIC (par défaut utilise KIMI_MODEL)
PLAN_BASIC_LLM_MODEL=moonshot-v1-32k

# Override modèle pour plan PRO (par défaut utilise OPENAI_MODEL)
PLAN_PRO_LLM_MODEL=gpt-4o-mini

# Override modèle pour plan ENTERPRISE (par défaut utilise ANTHROPIC_MODEL)
PLAN_ENTERPRISE_LLM_MODEL=claude-3-opus-20240229
```

---

## Exemples d'Usage

### Exemple 1 : Utiliser Kimi avec modèle 32K au lieu de 128K

Dans `.env` :
```bash
KIMI_API_KEY=sk-xxx
KIMI_MODEL=moonshot-v1-32k  # ← Change de 128K à 32K
```

Puis redémarrer :
```bash
docker-compose restart genesis-api
```

### Exemple 2 : Forcer GPT-4o-mini pour le plan BASIC

Dans `.env` :
```bash
PLAN_BASIC_LLM_MODEL=gpt-4o-mini
```

⚠️ **Important :** Vérifier que `OPENAI_API_KEY` est configuré !

### Exemple 3 : Tester un nouveau modèle Kimi

```bash
# Ajouter dans .env
KIMI_MODEL=moonshot-v1-8k  # Nouveau modèle

# Redémarrer
docker-compose restart genesis-api

# Vérifier logs
docker logs genesis-api --tail 50 | grep "KimiLLMProvider"
```

---

## Architecture Technique

### Hiérarchie de Configuration

```
1. settings.py (définit modèles par défaut)
   ↓
2. .env (override les valeurs par défaut)
   ↓
3. config.py (utilise settings pour générer mapping dynamique)
   ↓
4. factory.py (crée les providers avec bons modèles)
```

### Fichiers Concernés

- **`app/config/settings.py`** : Variables d'environnement (KIMI_MODEL, PLAN_BASIC_LLM_MODEL, etc.)
- **`app/core/providers/config.py`** : Mapping plan → provider/modèle (génération dynamique)
- **`app/core/providers/factory.py`** : Instanciation des providers avec configuration

---

## Validation

### Vérifier la Configuration Active

```bash
# Logs au démarrage du container
docker logs genesis-api --tail 100 | grep -E "(KimiLLMProvider|DeepseekProvider|model)"

# Rechercher ligne :
# "Création LLM provider" avec model=moonshot-v1-128k
# "KimiLLMProvider initialized" avec model=moonshot-v1-128k
```

### Test Rapide

1. Créer session coaching : `POST /api/v1/coaching/start`
2. Envoyer réponse : `POST /api/v1/coaching/step`
3. Vérifier logs : `docker logs genesis-api --tail 30`
4. Chercher : `"Kimi generate request"` ou `"Deepseek generate request"`

---

## Troubleshooting

### Erreur : `MockLLMProvider` utilisé au lieu de Kimi

**Cause :** `KIMI_API_KEY` non défini ou invalide dans `.env`

**Solution :**
```bash
# Vérifier .env
grep KIMI_API_KEY .env

# Doit retourner :
# KIMI_API_KEY=sk-xxx  (pas "your-kimi-key")

# Si manquant, ajouter :
echo "KIMI_API_KEY=sk-votre_vraie_cle" >> .env

# Redémarrer
docker-compose restart genesis-api
```

### Erreur : Modèle non reconnu

**Symptôme :** `Invalid model: moonshot-v1-xxx`

**Solution :** Vérifier les modèles supportés sur la doc provider :
- Kimi : https://platform.moonshot.cn/docs
- DeepSeek : https://platform.deepseek.com/api-docs

### Ancien modèle toujours utilisé après changement `.env`

**Cause :** Python cache le module `config.py` en mémoire

**Solution :**
```bash
# Restart simple ne suffit pas toujours
docker-compose down genesis-api
docker-compose up -d genesis-api
```

---

## Rollback (Retour DeepSeek)

Pour revenir à DeepSeek comme avant ADR-007 :

```bash
# Dans .env, modifier :
PLAN_BASIC_LLM_MODEL=deepseek-chat

# Redémarrer
docker-compose restart genesis-api
```

Ou modifier directement `config.py` ligne 45 :
```python
"llm_provider": "deepseek",
"llm_model": settings.PLAN_BASIC_LLM_MODEL or settings.DEEPSEEK_MODEL,
```

---

## Références

- **ADR-007** : Décision de switch DeepSeek → Kimi (22/12/2025)
- **settings.py** : Variables d'environnement (lignes 93-102)
- **config.py** : Mapping plan/provider (lignes 24-68)
- **Modèles Kimi** : moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
