---
title: "Fix Incomplet: business_name Onboarding non transmis au site"
date: "2025-12-24"
priority: "Haute"
status: "bug_persiste"
tags: ["gen-wo-006", "onboarding", "transformer", "bug"]
---

# 🐛 Bug business_name Onboarding non affiché dans site généré

**Date:** 24 décembre 2025  
**Priorité:** 🔴 Haute  
**Statut:** Bug persistant après tentative de fix

---

## Symptôme

Le nom du projet saisi dans l'**Étape 0 Onboarding** n'apparaît pas dans le site généré.

**Test réalisé:**
- Onboarding: Nom saisi = **"La Terrasse d'Abidjan"**
- Site généré: Titre affiché = **"Projet Sans Nom"**

---

## Test E2E Complet (DC360 → Genesis)

### ✅ Ce qui fonctionne
| Étape | Statut |
|-------|--------|
| DC360 Hub → `/coaching/onboarding` | ✅ |
| Onboarding 3 champs (nom/secteur/logo) | ✅ |
| Redirection → `/coaching` | ✅ |
| Coaching 5 étapes (Vision → Offre) | ✅ |
| Génération site | ✅ |
| Preview `/preview/{sessionId}` | ✅ |

### ❌ Ce qui ne fonctionne pas
- `business_name` saisi dans onboarding **n'apparaît PAS** dans le site
- Fallback hardcodé "Projet Sans Nom" utilisé à la place

---

## Analyse Technique

### Fix Tenté (Incomplet)

**Fichier modifié:** `c:\genesis\app\api\v1\coaching.py`

**Changement ligne 363-395:**
```python
async def _build_brief_from_coaching_steps(session_id: int, db: AsyncSession, session_data: Dict[str, Any] = None) -> Dict[str, Any]:
    # GEN-WO-006: Récupérer business_name et secteur depuis onboarding si disponible
    business_name = "Projet Sans Nom"  # Fallback
    industry_sector = "default"
    
    if session_data and "onboarding" in session_data:
        onboarding = session_data["onboarding"]
        business_name = onboarding.get("business_name") or business_name
        industry_sector = onboarding.get("sector_resolved") or onboarding.get("sector") or industry_sector
    
    brief = {
        "business_name": business_name,
        "industry_sector": industry_sector,
        ...
    }
```

**Tous les appels mis à jour:**
- Ligne 194: `brief_context = await _build_brief_from_coaching_steps(session_data["id"], db, session_data)`
- Ligne 288-291: `business_brief_dict = await _build_brief_from_coaching_steps(..., session_data=session_data)`
- Ligne 434: `brief = await _build_brief_from_coaching_steps(session_data["id"], db, session_data)`
- Ligne 492: `brief = await _build_brief_from_coaching_steps(session_data["id"], db, session_data)`

---

## Cause Racine Probable

### Hypothèse 1: Orchestrateur LangGraph Écrase les Données
**Ligne 295-300** (`coaching.py`):
```python
orchestrator = LangGraphOrchestrator()
orchestration_result = await orchestrator.run({
    "user_id": current_user.id,
    "brief_id": request.session_id,
    "business_brief": business_brief_dict  # ← Contient business_name correct
})
```

**Problème potentiel:**
L'orchestrateur pourrait **regénérer/écraser** le `business_name` dans le brief final avant de le passer au Transformer.

### Hypothèse 2: Redis session_data Ne Contient Pas l'Onboarding
Si les données d'onboarding ne sont **pas présentes dans Redis** au moment de la génération, le fallback s'applique.

**Vérification requise:**
```python
session_data_json = await redis_client.get(f"session:{session_id}")
session_data = json.loads(session_data_json)
print(session_data.get("onboarding"))  # Doit contenir business_name
```

---

## Solution Recommandée

### Option A: Forcer business_name Après Orchestration (Quick Fix)
**Fichier:** `c:\genesis\app\api\v1\coaching.py`  
**Ligne:** ~306 (après orchestration_result)

```python
# 3. Forcer business_name depuis onboarding (GEN-WO-006 Fix)
if session_data and "onboarding" in session_data:
    onboarding = session_data["onboarding"]
    if onboarding.get("business_name"):
        orchestration_result["business_brief"]["business_name"] = onboarding["business_name"]
    if onboarding.get("sector_resolved") or onboarding.get("sector"):
        orchestration_result["business_brief"]["industry_sector"] = onboarding.get("sector_resolved") or onboarding.get("sector")

# 4. Transformer en SiteDefinition (avec business_name corrigé)
enriched_brief = BusinessBriefData(
    business_name=orchestration_result["business_brief"]["business_name"],
    ...
)
```

### Option B: Passer Onboarding à l'Orchestrateur (Propre)
**Fichier:** `c:\genesis\app\api\v1\coaching.py`  
**Ligne:** ~296

```python
orchestrator = LangGraphOrchestrator()
orchestration_result = await orchestrator.run({
    "user_id": current_user.id,
    "brief_id": request.session_id,
    "business_brief": business_brief_dict,
    "onboarding": session_data.get("onboarding", {})  # ← Nouveau
})
```

**Puis dans l'orchestrateur:**
- Préserver `business_name` et `sector` de l'onboarding
- Ne pas les regénérer via LLM

---

## Tests de Validation

### Protocole
1. Login DC360 Hub (`dcitest@digital.ci`)
2. Cliquer "Lancer Genesis"
3. Onboarding: Saisir **"Restaurant Chez Fatou"**
4. Compléter coaching (5 étapes)
5. Cliquer "Voir mon site"
6. **✅ Vérifier:** Titre = "Bienvenue chez Restaurant Chez Fatou"

### Résultat Attendu
```
Hero Title: "Bienvenue chez Restaurant Chez Fatou"
About Section: "Restaurant Chez Fatou"
Footer: "© 2025 Restaurant Chez Fatou. Tous droits réservés."
```

---

## Impact

**Sans fix:**
- ❌ UX dégradée (tous les sites affichent "Projet Sans Nom")
- ❌ Perte de personnalisation
- ❌ Valeur de l'onboarding annulée

**Avec fix:**
- ✅ Sites personnalisés dès génération
- ✅ Onboarding valorisé
- ✅ Expérience utilisateur professionnelle

---

**Prochaine étape:** Implémenter Option A (quick fix) puis tester E2E complet
