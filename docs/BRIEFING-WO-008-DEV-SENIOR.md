# 📋 BRIEFING WO-008 - Pour Dev Senior

**Date :** 25/12/2025 02:00 UTC  
**De :** Tech Lead Genesis AI  
**À :** Dev Senior  
**Priorité :** 🔴 HAUTE  

---

## 🎯 Mission Rapide

Corriger la génération du site pour que le **business_name** sauvegardé lors de l'onboarding soit utilisé dans le site généré.

**Problème :** Site affiche "Projet Sans Nom" au lieu de "Pâtisserie Dakar Gold"

---

## ✅ Ce Qui Fonctionne Déjà

- ✅ **WO-006** : Backend fix `preserve_onboarding_on_save()` implémenté et validé
- ✅ **WO-007** : Erreurs d'images Next.js résolues
- ✅ **E2E complet** : DC360 → Genesis → Coaching → Site Preview (sans erreurs)
- ✅ **Onboarding** : "Pâtisserie Dakar Gold" sauvegardé correctement en Redis

---

## ❌ Le Problème

Lors de la génération du site, la fonction `_build_brief_from_coaching_steps()` ne récupère pas le `business_name` depuis l'onboarding.

**Résultat :** Brief créé sans business_name → Site généré avec "Projet Sans Nom"

---

## 🔧 Solution

**Fichier à modifier :** `c:\genesis\app\api\v1\coaching.py`

**Fonction :** `_build_brief_from_coaching_steps()` (ligne ~350-400)

**Fix simple :**
```python
# Ajouter au début de la fonction :
business_name = session_data.get('onboarding', {}).get('business_name', 'Projet Sans Nom')

# Inclure dans le brief retourné :
brief = {
    'business_name': business_name,  # ← AJOUTER CETTE LIGNE
    'vision': coaching_steps.get('vision', ''),
    'mission': coaching_steps.get('mission', ''),
    # ... reste du code
}
```

---

## 📊 Validation

**Test E2E :**
1. Login DC360 : `dcitest@digital.ci` / `DiGiT@l2025`
2. Lancer Genesis
3. Onboarding : Business Name = "Pâtisserie Dakar Gold"
4. Coaching : Vision → Mission → Clientèle → Différenciation → Offre
5. ✅ Vérifier que "Pâtisserie Dakar Gold" apparaît dans le site preview

**Commande Redis pour vérifier :**
```bash
docker exec redis redis-cli GET "session:a707a352-27fe-47e1-941d-7f58831a93ab" | jq '.onboarding.business_name'
```

---

## 📚 Documentation Complète

Voir : `c:\genesis\docs\work_orders\WO-008-FIX-BUSINESS-NAME-SITE-GENERATION-25DEC2025.md`

---

## ⏱️ Temps Estimé

**1-2 heures** (audit + fix + tests)

---

## 🚀 Prochaines Étapes

1. Lire le WO-008 complet
2. Auditer `_build_brief_from_coaching_steps()` 
3. Implémenter le fix
4. Tester E2E
5. Merger sur master avec tag `v1.0.0-phase1c`

---

**Bonne chance ! 💪**
