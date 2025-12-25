---
title: "Memo: Correction Lien Genesis dans DC360 Hub"
date: "2025-12-24"
priority: "Haute"
destinataire: "Architecte DC360 Hub"
emetteur: "Tech Lead Genesis AI"
tags: ["dc360", "genesis", "onboarding", "integration"]
---

# 🔗 Correction Lien Genesis dans DC360 Hub

**Date:** 24 décembre 2025  
**Priorité:** 🔴 Haute  
**Statut:** Action requise

---

## 🐛 Problème Identifié

Lors du test E2E du flow utilisateur depuis le DC360 Hub, l'**Étape 0 Onboarding** (GEN-WO-006 Phase A) est **complètement sautée**.

### Comportement Actuel (Incorrect)
```
DC360 Hub → Bouton "Lancer Genesis" → http://localhost:3002/coaching
```

**Impact utilisateur:**
- L'utilisateur arrive directement sur l'étape Vision
- **Aucune collecte** de : nom du projet, secteur d'activité, intention logo
- Le site généré affiche "Projet Sans Nom" au lieu du nom réel
- Mauvaise expérience utilisateur (contexte manquant)

### Comportement Attendu (Correct)
```
DC360 Hub → Bouton "Lancer Genesis" → http://localhost:3002/coaching/onboarding
```

---

## ✅ Solution

### Action Requise
**Modifier le lien du bouton "Lancer Genesis" dans le DC360 Hub Dashboard**

**Fichier à modifier:** Composant Dashboard DC360 (localisation exacte à déterminer côté Hub)

**Changement:**
```diff
- URL: http://localhost:3002/coaching
+ URL: http://localhost:3002/coaching/onboarding
```

### Justification
L'**Étape 0 Onboarding** est un prérequis obligatoire pour la Phase 2 du coaching (GEN-WO-006). Elle collecte les informations de base qui personnalisent toute l'expérience :
1. **Nom du projet** → utilisé dans le site généré
2. **Secteur d'activité** → adapte les questions et le design
3. **Logo** → Upload/Générer/Plus tard

---

## 🧪 Test de Validation

### Protocole de Test
1. Se connecter au DC360 Hub (`http://localhost:3000`)
   - Login: `dcitest@digital.ci`
   - Mot de passe: `DiGiT@l2025`
2. Cliquer sur **"Lancer Genesis"**
3. **✅ Vérifier** que l'URL est `http://localhost:3002/coaching/onboarding`
4. Compléter l'onboarding (3 questions)
5. Vérifier la redirection vers `/coaching` (Étape Vision)
6. Compléter les 5 étapes du coaching
7. Cliquer sur "Voir mon site"
8. **✅ Vérifier** que le nom du projet apparaît dans le site généré

### Résultat Attendu
Le flow complet doit être :
```
DC360 Hub → Onboarding (nom/secteur/logo) → Coaching (5 étapes) → Preview Site
```

---

## 📋 Contexte Technique

### Architecture GEN-WO-006 Phase A
- [x] Lien DC360 Hub modifié (`/coaching` → `/coaching/onboarding`)
- [x] Test E2E : DC360 → `/coaching/onboarding` fonctionne
- [x] Page onboarding affiche les 3 champs (nom, secteur, logo)
- [x] Test flow complet : Onboarding → Coaching 5 étapes → Preview 
- [x] **Bug identifié:** business_name non affiché (voir MEMO_FIX_BUSINESS_NAME_ONBOARDING_24DEC2025.md)
- [ ] Validation PO après fix bug business_name

### Fichiers Genesis Concernés
- Frontend: `genesis-frontend/src/app/coaching/onboarding/page.tsx`
- Backend: `app/api/v1/coaching.py` (endpoint onboarding)
- Composant: `genesis-frontend/src/components/LogoUploader.tsx`

---

## 📊 Impact Business

**Sans correction:**
- ❌ Mauvaise première impression (pas de personnalisation)
- ❌ Sites générés génériques ("Projet Sans Nom")
- ❌ Perte de contexte secteur (design non adapté)

**Avec correction:**
- ✅ Expérience utilisateur fluide et professionnelle
- ✅ Sites personnalisés dès le départ
- ✅ Questions adaptées au secteur métier
- ✅ Logo collecté ou généré automatiquement

---

## 🚀 Prochaines Étapes

1. **DC360 Hub:** Modifier le lien du bouton "Lancer Genesis"
2. **Test:** Valider le flow complet E2E
3. **Documentation:** Mettre à jour la doc d'intégration si nécessaire

---

**Contact Tech Lead Genesis:** Cascade  
**Validation requise par:** Product Owner  
**Deadline suggérée:** Avant activation Phase B (GEN-WO-006)
