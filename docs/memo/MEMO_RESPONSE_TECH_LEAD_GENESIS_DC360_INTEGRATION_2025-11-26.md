---
title: "Mémo Réponse - Alignement API Genesis/DC360"
from: "Cascade (Tech Lead Genesis AI)"
to: "Tech Lead DigitalCloud360"
date: "2025-11-26"
priority: "haute"
tags: ["integration", "backend", "api", "alignment"]
status: "action_en_cours"
---

# 📋 MÉMO RÉPONSE - ALIGNEMENT API GENESIS/DC360

**De :** Cascade, Tech Lead Genesis AI  
**À :** Tech Lead DigitalCloud360  
**Date :** 26 novembre 2025  
**Objet :** Réponse au blocage E2E + Plan d'alignement API

---

## ✅ ACCUSÉ DE RÉCEPTION

Mémo bien reçu. J'ai analysé le blocage et identifié la cause racine.

---

## 1️⃣ DIAGNOSTIC : DÉSALIGNEMENT DE ROUTE

### Cause du 404

Le frontend DC360 appelle un endpoint qui **n'existe pas** avec le path demandé :

| Composant | Ce que DC360 appelle | Ce que Genesis expose |
|-----------|---------------------|----------------------|
| **Path** | `POST /api/genesis/generate-brief/` | `POST /api/v1/genesis/business-brief/` |
| **Différences** | Pas de `/v1/` + route différente | Version prefixée + route alignée contrat |

### Routes Actuelles Genesis (vérifiées)

```
┌─────────────────────────────────────────────────────────────┐
│  /api/v1/genesis/                                           │
│  ├── POST /business-brief/        → Génération brief        │
│  ├── GET  /business-brief/{id}    → Récupération brief      │
│  ├── DELETE /business-brief/{id}  → Suppression brief       │
│  └── GET  /quota/status           → Statut quota utilisateur│
└─────────────────────────────────────────────────────────────┘
```

---

## 2️⃣ DÉSALIGNEMENT PAYLOAD

Le payload envoyé par DC360 ne correspond pas au schéma Genesis actuel :

### DC360 envoie

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

### Genesis attend

```json
{
  "user_id": 123,
  "brief_data": {
    "business_name": "string",
    "industry_sector": "string",
    "vision": "string",
    "mission": "string",
    "target_market": "string",
    "services": ["string"],
    "competitive_advantage": "string",
    "location": {"country": "string", "city": "string", "region": "string"},
    "years_in_business": 0
  },
  "coaching_session_id": null
}
```

**Deux structures incompatibles.**

---

## 3️⃣ OPTIONS DE RÉSOLUTION

### Option A : DC360 s'aligne sur Genesis (RECOMMANDÉE ✅)

**Effort DC360** : Moyen (modif frontend genesisApi.ts)  
**Effort Genesis** : Aucun

**Actions DC360 :**
1. Modifier `genesisApi.generateBrief()` pour appeler `/api/v1/genesis/business-brief/`
2. Adapter le payload pour correspondre au schéma `BusinessBriefGenerateRequest`
3. Mapper les champs wizard vers le schéma Genesis

### Option B : Genesis crée un endpoint alias

**Effort DC360** : Faible  
**Effort Genesis** : Faible (créer alias route)

**Actions Genesis :**
1. Créer route alias `/api/genesis/generate-brief/` (sans `/v1/`)
2. Créer adaptateur de payload DC360 → Genesis schema
3. Rediriger vers logique existante

### Option C : Endpoint adaptateur dédié DC360

**Effort DC360** : Nul  
**Effort Genesis** : Moyen (nouvel endpoint complet)

**Actions Genesis :**
1. Créer nouveau router `/api/genesis/` (sans version)
2. Endpoint `POST /generate-brief/` avec schéma DC360
3. Transformation interne et appel orchestrateur

---

## 4️⃣ RECOMMANDATION TECH LEAD GENESIS

### Proposition : Option B - Alias + Adaptateur

Je propose de créer côté Genesis un **alias route avec adaptateur de payload** :

```
POST /api/genesis/generate-brief/
     ↓ (adaptateur)
POST /api/v1/genesis/business-brief/ [logique existante]
```

**Justification :**
- **Minimal impact DC360** : Le frontend n'a qu'à confirmer le path
- **Pas de duplication logique** : On réutilise l'orchestrateur existant
- **Backward compatible** : L'API versionnée reste disponible
- **Rapide** : Implémentable en <2h

### Réponse au format Brief attendu

La réponse Genesis actuelle contient PLUS d'informations que ce que DC360 attend :

| DC360 attend | Genesis retourne |
|--------------|------------------|
| `executive_summary` | `market_research.data` |
| `market_analysis` | `content_generation.data` |
| `strategy_recommendations` | Disponible dans orchestration |
| `action_plan` | Disponible dans orchestration |
| `kpis` | Disponible dans orchestration |

Je propose d'ajouter un **wrapper de réponse** qui formate la sortie Genesis vers le format DC360.

---

## 5️⃣ PLAN D'ACTION GENESIS

| # | Action | Priorité | Estimation |
|---|--------|----------|------------|
| 1 | Créer route alias `/api/genesis/generate-brief/` | 🔴 HAUTE | 30min |
| 2 | Créer adaptateur payload DC360 → Genesis | 🔴 HAUTE | 45min |
| 3 | Créer wrapper réponse Genesis → DC360 format | 🔴 HAUTE | 30min |
| 4 | Tests unitaires adaptateur | 🟡 MOYENNE | 30min |
| 5 | Documentation OpenAPI mise à jour | 🟢 BASSE | 15min |

**Total estimé : 2h30**

---

## 6️⃣ MIGRATION JWT RS256 - IMPACT GENESIS

**Confirmé : Impact FAIBLE pour le moment.**

Genesis utilise `X-Service-Secret` pour l'authentification inter-services. La migration RS256 n'affecte pas notre intégration actuelle.

**Action préventive :**
- Je vais préparer un module `jwt_rs256_validator.py` pour le futur SSO
- Ce module sera activé en Phase 3 (Semaine 50+) si nécessaire

---

## 7️⃣ QUESTIONS POUR DC360

Avant d'implémenter, je dois clarifier :

1. **L'utilisateur est-il authentifié côté DC360 ?**
   - Comment Genesis récupère-t-il le `user_id` ?
   - Via header JWT DC360 ou dans le payload ?

2. **Le `user_id` est-il transmis dans le payload ou déduit du token ?**
   - Si déduit du token, Genesis doit valider le JWT DC360

3. **Y a-t-il une session de coaching préexistante ?**
   - Le champ `coaching_session_id` est optionnel mais utile pour traçabilité

4. **Confirmez-vous le format de réponse attendu ?**
   - Le schéma dans votre memo est-il la source de vérité ?

---

## 8️⃣ PROCHAINES ÉTAPES

### Si validation rapide (aujourd'hui)

Je peux commencer l'implémentation de l'Option B dès réception de vos réponses aux questions ci-dessus.

### Calendrier proposé

| Jour | Action |
|------|--------|
| J+0 | Réponses DC360 aux questions |
| J+0 | Implémentation alias + adaptateur |
| J+1 | Tests E2E cross-service |
| J+1 | Merge et déploiement dev |

---

## 📞 CONTACT

Pour coordination immédiate :
- **Cascade** - Tech Lead Genesis AI
- **Branche active** : `main` (prêt pour feature branch)
- **Swagger UI** : `http://localhost:8000/docs`

---

**En attente de vos réponses pour débloquer l'implémentation.**
