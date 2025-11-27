---
title: "Work Order - Correction Bug AgentException (Logo/SEO)"
code: "WO-GENESIS-FIX-AGENT-EXCEPTION-S3-002"
priority: "MOYENNE - QUALITÉ"
assignee: "Senior Developer Genesis"
reviewer: "Tech Lead Genesis (Cascade)"
date: "2025-11-27"
sprint: "Sprint 3 - Stabilisation"
estimated_effort: "1h"
tags: ["bugfix", "exception", "logo_agent", "seo_agent"]
status: "ready_for_dev"
---

# 🐛 WORK ORDER : Correction Bug AgentException

## Contexte

Lors du test E2E du 27/11/2025, bien que la génération de brief ait réussi globalement, des erreurs internes ont été détectées dans les logs pour les agents **Logo** et **SEO**.

Le message d'erreur est le suivant :
`AgentException.__init__() takes from 1 to 2 positional arguments but 3 were given`

Cela indique une erreur Python lors de la levée de l'exception elle-même (problème de signature dans le constructeur de `AgentException`).

## 🎯 Objectifs

1.  **Corriger l'appel à `AgentException`** dans les agents `logo_creation` et `seo_optimization`.
2.  **Vérifier la signature** de la classe `AgentException` dans `app/utils/exceptions.py` (ou équivalent).
3.  **Standardiser** la levée d'exceptions dans tous les sub-agents.

## 🛠️ Tâches Techniques

### 1. Analyse `app/utils/exceptions.py`
*   Vérifier le constructeur `__init__` de `AgentException`.
*   Confirmer s'il accepte `(message, detail=None)` ou autre.

### 2. Correction `app/core/agents/logo.py`
*   Identifier les endroits où `AgentException` est levée.
*   Corriger les arguments passés (probablement un argument de trop, comme un code erreur ou un contexte non supporté par le constructeur actuel).

### 3. Correction `app/core/agents/seo.py`
*   Même correction que pour l'agent Logo.

### 4. Vérification autres agents
*   Scanner rapidement `research.py`, `content.py`, `template.py` pour voir si l'erreur est présente ailleurs.

## ✅ Critères d'Acceptation (DoD)

- [ ] La classe `AgentException` est correctement instanciée partout.
- [ ] Les tests unitaires des agents (mockant une erreur) passent sans `TypeError` sur l'exception elle-même.
- [ ] Le code est pushé sur une branche `fix/agent-exception-signature`.

## 🧪 Tests Recommandés

Créer un petit test unitaire (ou ajuster l'existant) qui force une erreur dans l'agent Logo et vérifie que l'exception remontée est bien une `AgentException` propre, et non une erreur Python de constructeur.
