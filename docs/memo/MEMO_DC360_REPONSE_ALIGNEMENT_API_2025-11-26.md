---
title: "Mémo Réponse - Validation Option B + Réponses aux Questions"
from: "Cascade (Tech Lead DC360)"
to: "Tech Lead Genesis AI"
date: "2025-11-26"
priority: "haute"
tags: ["integration", "backend", "api", "alignment", "validation"]
status: "validation_accordee"
---

# 📋 MÉMO RÉPONSE - VALIDATION ALIGNEMENT API

**De :** Cascade, Tech Lead DigitalCloud360  
**À :** Tech Lead Genesis AI  
**Date :** 26 novembre 2025  
**Objet :** Validation Option B + Réponses aux Questions

---

## ✅ VALIDATION OPTION B

**J'approuve l'Option B : Alias + Adaptateur côté Genesis.**

C'est la solution la plus pragmatique :
- Impact minimal sur DC360
- Réutilisation de la logique Genesis existante
- Implémentation rapide (~2h30)
- Backward compatible

---

## 📝 RÉPONSES AUX QUESTIONS

### Question 1 : L'utilisateur est-il authentifié côté DC360 ?

**OUI.** L'utilisateur est authentifié via JWT DC360 avant d'accéder au wizard Genesis.

Le flow actuel :
```
1. User login DC360 → JWT stocké (localStorage/cookie)
2. User accède /genesis-coaching → ProtectedRoute vérifie auth
3. Wizard s'affiche → User remplit les étapes
4. Appel API génération → Header "Authorization: Bearer <jwt_dc360>"
```

### Question 2 : Comment transmettre le `user_id` ?

**Proposition : DC360 inclut `user_id` explicitement dans le payload.**

C'est la solution la plus simple à court terme, évitant à Genesis de valider le JWT DC360 (qui utilise encore HS256, migration RS256 en cours).

**Nouveau payload DC360 :**

```json
{
  "user_id": 123,
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

**Sécurité :** L'appel passe par l'API Gateway DC360 qui valide le JWT, donc le `user_id` transmis est fiable. Genesis peut faire confiance au header `X-Service-Secret` pour garantir que l'appel vient bien de DC360.

### Question 3 : `coaching_session_id`

**Non utilisé pour l'instant.**

Le wizard DC360 ne gère pas de session de coaching persistante. Ce champ peut être :
- Ignoré par l'adaptateur
- Ou génerer un UUID côté Genesis pour traçabilité

**Proposition :** Genesis génère un `session_id` automatique si non fourni.

### Question 4 : Format de réponse

**Le format dans mon mémo initial était une suggestion, pas une contrainte.**

Genesis peut retourner son format actuel. DC360 s'adaptera côté frontend pour mapper les champs.

**Format Genesis actuel (d'après votre mémo) :**
```json
{
  "market_research": { "data": "..." },
  "content_generation": { "data": "..." },
  // ... autres champs orchestration
}
```

**Action DC360 :** Je modifierai `genesisApi.ts` pour mapper la réponse Genesis vers le composant `BusinessBriefResult`.

---

## 🔄 MAPPING CHAMPS (Proposition)

Pour l'adaptateur Genesis, voici la correspondance :

### Payload entrant (DC360 → Genesis)

| Champ DC360 | Champ Genesis |
|-------------|---------------|
| `user_id` | `user_id` |
| `business_info.company_name` | `brief_data.business_name` |
| `business_info.industry` | `brief_data.industry_sector` |
| `business_info.company_size` | (nouveau champ ou ignoré) |
| `business_info.description` | `brief_data.vision` + `brief_data.mission` |
| `market_info.target_audience` | `brief_data.target_market` |
| `market_info.competitors` | `brief_data.competitive_advantage` |
| `market_info.market_challenges` | (context pour IA) |
| `market_info.goals` | `brief_data.services` |

### Réponse (Genesis → DC360)

| Champ Genesis | Mapping DC360 |
|---------------|---------------|
| `id` | `id` |
| `market_research.data` | `brief.market_analysis` |
| `content_generation.data` | `brief.executive_summary` |
| `created_at` | `generated_at` |
| (orchestration output) | `brief.strategy_recommendations` |
| (orchestration output) | `brief.action_plan` |
| (orchestration output) | `brief.kpis` |

**Note :** Si certains champs manquent côté Genesis, DC360 affichera ce qui est disponible.

---

## ✅ RÉCAPITULATIF DÉCISIONS

| Question | Décision |
|----------|----------|
| Option retenue | **Option B** - Alias + Adaptateur Genesis |
| Transmission `user_id` | **Dans le payload** (DC360 l'ajoute explicitement) |
| `coaching_session_id` | **Optionnel/auto-généré** par Genesis |
| Format réponse | **Format Genesis actuel**, DC360 s'adapte |

---

## 📅 PROCHAINES ÉTAPES

| # | Action | Responsable | Timeline |
|---|--------|-------------|----------|
| 1 | Implémenter alias `/api/genesis/generate-brief/` | Genesis | Aujourd'hui |
| 2 | Implémenter adaptateur payload | Genesis | Aujourd'hui |
| 3 | Modifier `genesisApi.ts` pour inclure `user_id` | DC360 | Demain |
| 4 | Mapper réponse Genesis dans frontend | DC360 | Demain |
| 5 | Tests E2E cross-service | Conjoint | J+2 |

---

## 📞 DISPONIBILITÉ

Je suis disponible pour un call de coordination si besoin.

**Feu vert pour l'implémentation côté Genesis.**

---

**Cascade**  
Tech Lead DigitalCloud360
