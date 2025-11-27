---
title: "Demande : Environnement de Test E2E Intégré (Docker)"
from: "Product Owner Genesis AI"
to: "Cascade - Ecosystem Scrum Master & Coordinator"
date: "27 novembre 2025"
status: "REQUEST"
tags: ["testing", "docker", "integration", "e2e"]
priority: "HIGH"
---

# 🛑 MÉMO : Pré-requis Test Manuel E2E

## 1. Contexte & Demande
Nous avons complété la Phase 1B (Moteur de Rendu). Le système est théoriquement capable de générer et afficher des sites.

En tant que PO, **je souhaite effectuer un test manuel complet** pour valider l'expérience avant d'autoriser la suite des développements (Phase 2 - Chat).
Je refuse les tests via scripts de contournement ("seed scripts"). Je veux tester **le système réel dans son environnement Docker**, comme en production.

## 2. Le Problème Technique (Isolation)
Actuellement, Genesis tourne dans sa propre stack Docker (`docker-compose.yml`) avec son réseau isolé `genesis-ai-network`.
Le Hub DC360 (SSO, Auth) tourne sur la même machine mais probablement dans un autre réseau Docker ou en local.

**Conséquence :**
Si je me connecte sur Genesis (`localhost:3000`), le SSO va échouer car le conteneur `genesis-api` ne peut pas valider le token auprès du conteneur `dc360-hub` (problème de visibilité réseau inter-conteneurs).

## 3. Action Requise du Coordinateur
Pour permettre ce test E2E "Prod-like", nous avons besoin de **connecter les deux mondes**.

Nous sollicitons une directive technique pour :
1.  Soit intégrer Genesis dans le `docker-compose` global de l'écosystème.
2.  Soit créer un **réseau Docker partagé** (ex: `digitalcloud360-network`) et y attacher Genesis.
3.  Fournir les URLs d'accès internes Docker du Hub (ex: `http://dc360-hub:8000`).

**L'objectif est simple :**
Je veux pouvoir me loguer sur le Hub, cliquer sur "Genesis", être redirigé, et que tout fonctionne de bout en bout sans "triche".

Dans l'attente de votre configuration réseau unifiée.
