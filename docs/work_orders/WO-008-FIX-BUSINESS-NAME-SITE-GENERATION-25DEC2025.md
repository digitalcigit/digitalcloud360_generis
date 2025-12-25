---
title: "WO-008 - Corriger la Génération du Site avec Business Name"
tags: ["backend", "coaching", "site-generation", "business-name", "redis"]
status: "ready"
date: "2025-12-25"
priority: "high"
---

# WO-008 : Corriger la Génération du Site avec Business Name

**Créé par :** Tech Lead Genesis AI  
**Date :** 25/12/2025 01:55 UTC  
**Assigné à :** Dev Senior  
**Priorité :** 🔴 HAUTE  
**Complexité :** MOYENNE  
**Temps Estimé :** 1-2h  

---

## 📋 Contexte

### Situation Actuelle
- ✅ **WO-006 (Fix Business Name)** : Implémenté et validé techniquement
  - Fonction `preserve_onboarding_on_save()` fonctionne correctement
  - Onboarding "Pâtisserie Dakar Gold" sauvegardé en Redis
  - E2E DC360 → Genesis complet et fonctionnel

- ✅ **WO-007 (Fix Images Next.js)** : Résolu
  - Erreurs d'images Next.js éliminées
  - Site preview s'affiche sans erreurs

- ❌ **Problème Identifié** : Site généré affiche "Projet Sans Nom" au lieu de "Pâtisserie Dakar Gold"
  - Le business_name n'est pas utilisé lors de la génération du site
  - Cause probable : Fonction `_build_brief_from_coaching_steps()` ne récupère pas le business_name depuis l'onboarding

### Validation E2E Effectuée
```
1. Login DC360 : dcitest@digital.ci / DiGiT@l2025
2. Lancer Genesis
3. Onboarding : Business Name = "Pâtisserie Dakar Gold"
4. Coaching : Vision → Mission → Clientèle → Différenciation → Offre
5. Résultat : Site généré avec "Projet Sans Nom" ❌
```

---

## 🎯 Objectif

Corriger la génération du site pour que le **business_name** sauvegardé lors de l'onboarding soit utilisé correctement lors de la création du brief et du site.

**Résultat attendu :** Site affiche "Pâtisserie Dakar Gold" au lieu de "Projet Sans Nom"

---

## 🔍 Analyse Technique

### Flux Actuel
```
1. Onboarding : business_name sauvegardé en Redis
   └─ session:{session_id}['onboarding']['business_name'] = "Pâtisserie Dakar Gold"

2. Coaching Steps : Données mises à jour via preserve_onboarding_on_save()
   └─ Onboarding préservé ✅

3. Fin du Coaching : Génération du site
   └─ Appel à _build_brief_from_coaching_steps()
   └─ Création du brief SANS le business_name ❌

4. Résultat : Site avec "Projet Sans Nom"
```

### Fichiers Impliqués
- **`c:\genesis\app\api\v1\coaching.py`** (PRINCIPAL)
  - Fonction `_build_brief_from_coaching_steps()` (ligne ~350-400)
  - Fonction `process_coaching_step()` (ligne ~170-280)
  - Endpoint `/end` (fin du coaching)

- **`c:\genesis\app\api\v1\site_generator.py`** (À VÉRIFIER)
  - Fonction de génération du site
  - Utilisation du brief pour créer le site

---

## 📝 Tâches à Effectuer

### 1️⃣ Audit du Code - Identifier le Problème

**Fichier :** `c:\genesis\app\api\v1\coaching.py`

**À vérifier :**
```python
# Fonction _build_brief_from_coaching_steps()
# Questions clés :
# 1. Récupère-t-elle session_data['onboarding']['business_name'] ?
# 2. Utilise-t-elle business_name dans le brief ?
# 3. Passe-t-elle le business_name au site_generator ?
```

**Ligne de recherche :**
```bash
grep -n "_build_brief_from_coaching_steps" c:\genesis\app\api\v1\coaching.py
grep -n "business_name" c:\genesis\app\api\v1\coaching.py
```

### 2️⃣ Correction - Implémenter le Fix

**Approche :**

A. **Dans `_build_brief_from_coaching_steps()` :**
```python
async def _build_brief_from_coaching_steps(session_data: Dict[str, Any], redis_client: redis.Redis) -> Dict[str, Any]:
    """Construire le brief à partir des étapes du coaching"""
    
    # ✅ AJOUTER : Récupérer le business_name depuis l'onboarding
    business_name = session_data.get('onboarding', {}).get('business_name', 'Projet Sans Nom')
    
    # Récupérer les étapes du coaching
    coaching_steps = session_data.get('coaching_steps', {})
    
    # Construire le brief
    brief = {
        'business_name': business_name,  # ✅ INCLURE LE BUSINESS_NAME
        'vision': coaching_steps.get('vision', ''),
        'mission': coaching_steps.get('mission', ''),
        'target_audience': coaching_steps.get('clientele', ''),
        'differentiation': coaching_steps.get('differentiation', ''),
        'offerings': coaching_steps.get('offre', ''),
        # ... autres champs
    }
    
    return brief
```

B. **Vérifier la propagation :**
- Le brief contenant `business_name` est-il passé au `site_generator` ?
- Le `site_generator` utilise-t-il `brief['business_name']` pour créer le site ?

### 3️⃣ Validation - Tests

**Test Unitaire :**
```python
# Dans test_business_name_fix.py ou nouveau test
async def test_build_brief_includes_business_name():
    """Vérifier que _build_brief_from_coaching_steps inclut le business_name"""
    
    session_data = {
        'onboarding': {
            'business_name': 'Pâtisserie Dakar Gold',
            'industry_sector': 'Food & Beverage'
        },
        'coaching_steps': {
            'vision': 'Devenir la meilleure pâtisserie...',
            'mission': 'Offrir des pâtisseries...',
            # ...
        }
    }
    
    brief = await _build_brief_from_coaching_steps(session_data, redis_client)
    
    assert brief['business_name'] == 'Pâtisserie Dakar Gold'
    assert brief['business_name'] != 'Projet Sans Nom'
```

**Test E2E :**
```
1. Lancer E2E depuis DC360 (http://localhost:3000/login)
2. Onboarding avec "Pâtisserie Dakar Gold"
3. Compléter coaching (Vision → Offre)
4. Naviguer vers preview
5. ✅ Vérifier que "Pâtisserie Dakar Gold" apparaît dans le site
```

### 4️⃣ Déploiement

**Étapes :**
1. Commit des changements sur branche `feature/wo-008-business-name-generation`
2. Tests unitaires passent ✅
3. Tests E2E passent ✅
4. Merge sur `master`
5. Tag version : `v1.0.0-phase1c`

---

## 🔧 Checklist Technique

### Avant de Commencer
- [ ] Lire le code de `_build_brief_from_coaching_steps()` complètement
- [ ] Identifier où le business_name est perdu
- [ ] Vérifier le flux complet : onboarding → coaching → site_generator

### Implémentation
- [ ] Ajouter récupération du business_name depuis session_data['onboarding']
- [ ] Inclure business_name dans le brief retourné
- [ ] Vérifier que site_generator utilise brief['business_name']
- [ ] Ajouter logging pour tracer le business_name

### Tests
- [ ] Test unitaire : `_build_brief_from_coaching_steps()` inclut business_name
- [ ] Test E2E : Site affiche "Pâtisserie Dakar Gold"
- [ ] Vérifier pas de régression sur autres sites

### Documentation
- [ ] Ajouter commentaires explicatifs dans le code
- [ ] Mettre à jour la documentation technique si nécessaire
- [ ] Documenter la solution dans ce WO

---

## 📊 Critères d'Acceptation

✅ **SUCCÈS** si :
1. Site généré affiche le business_name correct ("Pâtisserie Dakar Gold")
2. Pas de régression : autres sites continuent de fonctionner
3. Tests unitaires et E2E passent
4. Code reviewé et mergé sur master
5. Documentation mise à jour

❌ **ÉCHEC** si :
1. Site affiche toujours "Projet Sans Nom"
2. Tests E2E échouent
3. Régression sur d'autres fonctionnalités

---

## 📚 Ressources

**Fichiers clés :**
- `@c:\genesis\app\api\v1\coaching.py:350-400` - Fonction `_build_brief_from_coaching_steps()`
- `@c:\genesis\app\api\v1\coaching.py:170-280` - Fonction `process_coaching_step()`
- `@c:\genesis\test_business_name_fix.py` - Tests existants

**Commandes utiles :**
```bash
# Vérifier les données en Redis
docker exec redis redis-cli GET "session:a707a352-27fe-47e1-941d-7f58831a93ab" | jq '.onboarding.business_name'

# Lancer les tests
cd c:\genesis && python -m pytest test_business_name_fix.py -v

# Lancer E2E
cd c:\genesis\genesis-frontend && npm run test:e2e
```

---

## 🎯 Livrables

1. **Code :** Modifications dans `coaching.py` avec business_name inclus
2. **Tests :** Tests unitaires et E2E validant le fix
3. **Documentation :** Ce WO complété avec résultats
4. **Commit :** PR avec description claire du fix

---

## 📞 Support

**Questions ?** Consulter :
- Checkpoint WO-006 : Fix Business Name Onboarding
- Checkpoint WO-007 : Fix Images Next.js
- Mémoire : "WO-007 Completion - Next.js Image Configuration Fix"

**Contact :** Tech Lead Genesis AI

---

---

## 🎉 RÉSOLUTION FINALE (25/12/2025 09:35 UTC)

### ✅ WO-008 COMPLÉTÉ PAR DEV SENIOR

**Root Cause Identifiée :**
Le problème n'était PAS dans `_build_brief_from_coaching_steps()` comme supposé, mais dans le **frontend** :
- Onboarding appelait `/start` avec `session_id`, puis redirige vers `/coaching` **sans** passer le `session_id`
- `CoachingInterface` appelait `/start` à nouveau **sans** `session_id` → nouvelle session créée sans données d'onboarding

### 🔧 Fix Appliqué

**1. Onboarding Page - Passer session_id via URL**
```typescript
// @c:\genesis\genesis-frontend\src\app\coaching\onboarding\page.tsx:71-73
const res = await coachingApi.onboarding(token, payload);
router.push(`/coaching?session_id=${res.session_id}`);  // ← AJOUT session_id
```

**2. CoachingInterface - Lire et utiliser session_id**
```typescript
// @c:\genesis\genesis-frontend\src\components\coaching\CoachingInterface.tsx:42-48,82-83
const searchParams = useSearchParams();
const urlSessionId = searchParams.get('session_id');  // ← LECTURE depuis URL
// ...
const response = await coachingApi.start(
  token!, 
  urlSessionId ? { session_id: urlSessionId } : undefined  // ← UTILISATION
);
```

### 📊 Validation E2E ✅

**Input :** "Pâtisserie Dakar Gold" pendant l'onboarding

**Output :** Site preview affiche correctement le business_name dans :
- ✅ **Hero :** "Bienvenue chez Pâtisserie Dakar Gold"
- ✅ **Section About**
- ✅ **Footer :** "© 2025 Pâtisserie Dakar Gold"

### 📈 Impact

- ✅ **WO-006** (Backend Fix) : Était correct dès le départ
- ✅ **WO-007** (Images Fix) : Résolu avec succès
- ✅ **WO-008** (Génération Site) : Résolu - problème était dans le frontend
- ✅ **E2E Complet** : DC360 → Genesis → Coaching → Site Preview (business_name visible)

---

**Completion Date :** 25/12/2025 09:35 UTC  
**Status :** ✅ COMPLETED  
**Assignee :** Dev Senior  
**Resolution :** Frontend routing fix - session_id propagation
