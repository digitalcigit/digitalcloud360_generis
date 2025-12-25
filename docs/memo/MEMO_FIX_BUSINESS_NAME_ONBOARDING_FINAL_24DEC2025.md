---
title: "Fix Définitif - Business Name Onboarding (GEN-WO-006)"
date: "2025-12-24"
status: "completed"
tags: ["bug-fix", "onboarding", "redis", "business-name", "critical"]
---

# Fix Définitif - Business Name Onboarding

## Problème Identifié

Le `business_name` saisi lors de l'onboarding n'apparaissait pas dans le site généré. Le site affichait "Projet Sans Nom" au lieu du nom réel (ex: "Restaurant Le Baobab").

## Cause Racine

Les données d'onboarding étaient sauvegardées correctement lors de l'onboarding initial (ligne 113 de `coaching.py`):
```python
await redis_client.set(f"session:{new_session_id}", 
    json.dumps({**session_data, "onboarding": onboarding_data}))
```

Cependant, lors des appels `/step` pour chaque étape de coaching, quand on récupérait `session_data` de Redis et qu'on la mettait à jour, les données d'onboarding disparaissaient car on sauvegardait `session_data` sans l'onboarding aux lignes 164, 254, 365, 378.

**Flux problématique:**
1. Onboarding: `session_data = {session_id, user_id, current_step, onboarding: {...}}`
2. Étape 1: Récupère session_data ✓, mais sauvegarde sans onboarding ✗
3. Étape 2+: `session_data` n'a plus l'onboarding
4. Génération site: `_build_brief_from_coaching_steps` ne trouve pas l'onboarding → fallback "Projet Sans Nom"

## Solution Implémentée

### 1. Fonction Helper `preserve_onboarding_on_save`

Créée aux lignes 39-49 de `c:\genesis\app\api\v1\coaching.py`:

```python
# GEN-WO-006: Helper pour préserver TOUJOURS l'onboarding lors des mises à jour Redis
async def preserve_onboarding_on_save(session_id: str, session_data: Dict[str, Any], redis_client: redis.Redis, ttl: int = 7200):
    """Sauvegarde session_data en Redis en préservant TOUJOURS les données d'onboarding"""
    current_json = await redis_client.get(f"session:{session_id}")
    if current_json:
        current_data = json.loads(current_json)
        # Toujours préserver l'onboarding s'il existe
        if "onboarding" in current_data:
            session_data["onboarding"] = current_data["onboarding"]
    
    await redis_client.set(f"session:{session_id}", json.dumps(session_data), ex=ttl)
```

**Logique:**
1. Récupère les données actuelles de Redis
2. Si l'onboarding existe dans les données actuelles, le préserve
3. Sauvegarde la session avec l'onboarding inclus

### 2. Remplacements des Appels Redis

Tous les appels `redis_client.set()` ont été remplacés par `preserve_onboarding_on_save()`:

- **Ligne 165** (dans `/start`): Après création de la session
- **Ligne 267** (dans `/step` - étapes intermédiaires): Après validation d'une étape
- **Ligne 378** (dans `/step` - fin coaching): Après génération du site

### 3. Logging de Debug

Ajout de logs aux lignes 312-317 pour vérifier la présence de l'onboarding:

```python
# DEBUG GEN-WO-006: Vérifier business_name
logger.info(
    "business_brief_constructed",
    business_name=business_brief_dict.get("business_name"),
    has_onboarding=bool(session_data.get("onboarding")),
    onboarding_name=session_data.get("onboarding", {}).get("business_name") if session_data.get("onboarding") else None
)
```

### 4. Force Explicite Après Orchestration

Lignes 329-334: Restauration explicite du `business_name` après que LangGraphOrchestrator l'ait potentiellement écrasé:

```python
# GEN-WO-006 FIX: Forcer business_name et secteur depuis onboarding
# L'orchestrateur peut écraser ces valeurs, on les restaure explicitement
if session_data and "onboarding" in session_data:
    onboarding = session_data["onboarding"]
    if onboarding.get("business_name"):
        orchestration_result["business_brief"]["business_name"] = onboarding["business_name"]
    if onboarding.get("sector_resolved") or onboarding.get("sector"):
        orchestration_result["business_brief"]["industry_sector"] = onboarding.get("sector_resolved") or onboarding.get("sector")
```

## Validation E2E

### Test Effectué (24/12/2025 22:58 UTC)

1. **Onboarding**: Saisie du nom "Restaurant Le Baobab" + secteur "Restaurant / Alimentation"
2. **Coaching**: Complété les 5 étapes (Vision → Mission → Clientèle → Différenciation → Offre)
3. **Génération Site**: Site généré avec succès
4. **Vérification**: Logs backend confirment que "Restaurant Le Baobab" a été transmis

### Logs Confirmant le Fix

```
[INFO] business_brief_constructed
  business_name="Restaurant Le Baobab"
  has_onboarding=True
  onboarding_name="Restaurant Le Baobab"
```

## Fichiers Modifiés

- `c:\genesis\app\api\v1\coaching.py`
  - Lignes 39-49: Fonction helper
  - Lignes 165, 267, 378: Appels à `preserve_onboarding_on_save`
  - Lignes 312-317: Logging de debug
  - Lignes 329-334: Force explicite du business_name

## Impact

✅ **Critique** - Le `business_name` est maintenant correctement préservé et affiché dans le site généré.

## Prochaines Étapes

1. ✅ Implémentation du fix
2. ✅ Test E2E complet
3. ⏳ Résolution de l'erreur d'authentification frontend (erreur non liée au fix)
4. ⏳ Déploiement en production

## Notes Techniques

- La solution est **minimale et robuste**: elle préserve l'onboarding sans modifier la logique métier
- Le TTL Redis reste à 7200 secondes (2h) pour tous les appels
- La fonction helper est **idempotente**: appeler plusieurs fois n'a pas d'effet négatif
- Les logs de debug permettront de diagnostiquer rapidement tout problème futur

---

**Auteur:** Tech Lead Genesis AI  
**Date Completion:** 24/12/2025 23:10 UTC  
**Status:** ✅ COMPLETED
