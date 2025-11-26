---
title: "Mémo Technique - Intégration DC360/Genesis - Blocages & Actions Requises"
from: "Cascade (Tech Lead DC360)"
to: "Tech Lead Genesis AI"
date: "2025-11-26"
priority: "haute"
tags: ["integration", "backend", "api", "jwt", "rs256"]
status: "en_attente_action"
---

# 📋 MÉMO TECHNIQUE - INTÉGRATION DC360/GENESIS

**De :** Cascade, Tech Lead DigitalCloud360  
**À :** Tech Lead Genesis AI  
**Date :** 26 novembre 2025  
**Objet :** Blocage E2E Frontend + Migration JWT RS256

---

## 🎯 RÉSUMÉ EXÉCUTIF

Les tests E2E du wizard Genesis intégré dans DC360 sont **bloqués sur un endpoint backend manquant**. Parallèlement, une **migration JWT vers RS256** est en cours côté DC360 avec des implications pour Genesis.

---

## 1️⃣ BLOCAGE BACKEND - GÉNÉRATION BRIEF

### Contexte

Le frontend DC360 intègre désormais le wizard Genesis complet :
- ✅ Carte "Genesis AI Coach" visible sur le Dashboard DC360
- ✅ Navigation vers `/genesis-coaching`
- ✅ Wizard 4 étapes fonctionnel (BusinessInfoStep → MarketInfoStep → AIGenerationStep → ResultsStep)
- ❌ **Génération du brief échoue** : Erreur "Ressource introuvable" (404)

### Endpoint Attendu

Le frontend appelle `genesisApi.generateBrief()` qui cible :

```
POST /api/genesis/generate-brief/
```

**Payload envoyé :**

```json
{
  "business_info": {
    "company_name": "string",
    "industry": "string",
    "company_size": "string",
    "description": "string"
  },
  "market_info": {
    "target_audience": "string",
    "competitors": ["string"],
    "market_challenges": "string",
    "goals": ["string"]
  }
}
```

**Réponse attendue :**

```json
{
  "id": "uuid",
  "brief": {
    "executive_summary": "string",
    "market_analysis": "string",
    "strategy_recommendations": ["string"],
    "action_plan": ["string"],
    "kpis": ["string"]
  },
  "generated_at": "ISO8601",
  "tokens_used": "number"
}
```

### Action Requise

**Implémenter l'endpoint `/api/genesis/generate-brief/`** côté Genesis backend avec :
- Authentification via `X-Service-Secret` (déjà configuré pour `/api/genesis/subscription/`)
- Validation du quota utilisateur
- Appel au modèle IA pour génération
- Retour structuré du brief

### Priorité

🔴 **HAUTE** - Bloquant pour la finalisation de l'intégration DC360/Genesis

---

## 2️⃣ MIGRATION JWT RS256 - IMPLICATIONS GENESIS

### Contexte

DC360 migre son authentification JWT de **HS256** (symétrique) vers **RS256** (asymétrique) pour supporter le SSO multi-apps (Skills Coach AI, Genesis, futures apps).

### Ce qui change

| Aspect | Avant (HS256) | Après (RS256) |
|--------|---------------|---------------|
| **Clé de signature** | Secret partagé | Clé privée (DC360 only) |
| **Validation tokens** | Secret partagé | Clé publique (disponible) |
| **Endpoint clés** | N/A | `/.well-known/jwks.json` |
| **Sécurité** | Apps peuvent créer des tokens | Apps peuvent seulement valider |

### Impact pour Genesis

**Impact direct : FAIBLE** - Genesis utilise actuellement `X-Service-Secret` pour l'API gateway, pas la validation JWT.

**Impact futur : MOYEN** - Si Genesis doit valider des tokens JWT DC360 directement (ex: SSO utilisateur), il devra :

1. Récupérer la clé publique depuis `https://dc360.domain/.well-known/jwks.json`
2. Valider les tokens avec l'algorithme RS256
3. Extraire les claims (`user_id`, `organization_id`, `tenant_slug`)

### Exemple de validation Python

```python
import jwt
import requests
from jwt import PyJWKClient

JWKS_URL = "https://dc360.domain/.well-known/jwks.json"

def validate_dc360_token(token: str) -> dict:
    """Valide un token JWT DC360 avec la clé publique JWKS."""
    jwks_client = PyJWKClient(JWKS_URL)
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    
    decoded = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience="genesis"  # optionnel, si DC360 ajoute l'audience
    )
    return decoded
```

### Timeline

- **Semaine 48** : Implémentation RS256 côté DC360
- **Semaine 49** : POC SSO avec Skills Coach AI
- **Semaine 50+** : Extension SSO Genesis (si besoin)

---

## 📊 RÉCAPITULATIF ACTIONS

| # | Action | Responsable | Priorité | Deadline |
|---|--------|-------------|----------|----------|
| 1 | Implémenter `/api/genesis/generate-brief/` | Équipe Genesis | 🔴 HAUTE | ASAP |
| 2 | Préparer validation JWT RS256 (si SSO prévu) | Équipe Genesis | 🟡 MOYENNE | Semaine 50 |
| 3 | Confirmer format brief attendu | Tech Lead Genesis | 🟢 BASSE | 48h |

---

## 📞 CONTACT

Pour toute question ou coordination :
- **Cascade** - Tech Lead DC360
- **Branche active DC360** : `feature/genesis-ui-restore`
- **Dernier commit** : `b213613` - fix(genesis): Correction detection plans Genesis AI

---

**Merci de confirmer la réception de ce mémo et de fournir une estimation pour l'implémentation de l'endpoint génération brief.**
