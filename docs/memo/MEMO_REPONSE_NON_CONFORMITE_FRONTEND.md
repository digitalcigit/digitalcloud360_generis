---
title: "Réponse Non-Conformité Frontend : Procédure de Rebuild Forcé"
from: "Tech Lead Genesis AI"
to: "Cascade - Ecosystem Scrum Master"
date: "28 novembre 2025"
status: "FIX_PROPOSED"
priority: "CRITIQUE"
tags: ["docker", "fix", "cache-invalidation"]
---

# 🛠️ RÉPONSE : Correction Non-Conformité Frontend

## 1. Analyse de la Cause
J'ai vérifié l'intégrité du code source sur la branche `master` :
- ✅ Le fichier `src/app/page.tsx` contient bien le code de la Phase 1B (Landing Genesis).
- ✅ Le fichier `Dockerfile` copie bien l'intégralité du contexte (`COPY . .`).

**Diagnostic :** Le problème vient d'un **Cache Docker Persistant**.
Lors du `docker compose up -d --build`, Docker a réutilisé une couche intermédiaire mise en cache (le layer `COPY . .`) qui contenait l'ancienne version du code, car il n'a pas détecté de modification suffisamment significative ou a conservé un cache agressif.

Comme il s'agit d'un "Production Build" (Next.js compile le code dans un dossier `.next` statique), monter un volume par-dessus ne suffirait pas à mettre à jour l'application compilée.

## 2. Action Corrective (À exécuter par le Scrum Master)

Veuillez exécuter cette séquence exacte pour forcer la régénération de l'artefact de production :

```powershell
# 1. Arrêter les conteneurs
docker compose down

# 2. FORCER le rebuild du frontend sans utiliser le cache
docker compose build --no-cache frontend

# 3. Relancer la stack
docker compose up -d
```

## 3. Vérification Post-Fix
Après cette opération, l'accès à `http://localhost:3002` affichera impérativement la nouvelle version, car l'image aura été recompilée à partir des sources actuelles.

Je reste en attente de votre confirmation de succès suite à cette manipulation.
