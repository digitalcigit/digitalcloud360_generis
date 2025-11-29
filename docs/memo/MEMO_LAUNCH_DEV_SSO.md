---
title: "Ordre de Mission : Implémentation SSO Token Passing"
from: "Tech Lead"
to: "Frontend Squad"
date: "29 novembre 2025"
priority: "IMMEDIATE"
status: "LAUNCHED"
---

# 🚀 ORDRE DE MISSION : SSO Token Passing

## 🎯 Contexte
Pour fluidifier le test E2E et l'expérience de développement local, nous devons permettre le passage du token d'authentification via l'URL entre le Hub et Genesis.

## 📋 Ta Mission
Implémenter le mécanisme de réception et de stockage du token dans la Landing Page de Genesis.

**Référence Technique Absolue :**
👉 `docs/work_order/WO-GENESIS-SSO-TOKEN-PASSING.md`

## 🛠️ Instructions d'Exécution
1.  Partir de la branche `master` (à jour).
2.  Créer la branche `feature/frontend-sso-token`.
3.  Modifier `src/app/page.tsx` pour intercepter `?token=...`.
4.  **Critère de succès :** Le token doit être stocké en cookie/localStorage et l'URL nettoyée sans rechargement visible.

**Délai :** ASAP.

Bon code ! 👨‍💻
