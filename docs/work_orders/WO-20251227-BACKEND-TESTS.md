---
title: "WO-20251227: Stabilisation des Tests Unitaires Coaching (Backend)"
type: "Work Order"
priority: "High"
assignee: "Senior Backend Dev"
status: "Pending"
date: "2025-12-28"
---

# Work Order: Stabilisation des Tests Unitaires Coaching

## 1. Contexte
Le module "Coaching" (Phase 2 - Agents Premium) est fonctionnel en E2E, mais la suite de tests unitaires `tests/test_api/test_coaching.py` échoue actuellement dans l'environnement Docker CI/CD.
Le Tech Lead a identifié un problème d'isolation des dépendances Redis lors des tests.

## 2. Problème Identifié
Les tests échouent avec des erreurs liées à Redis (connexion ou données manquantes) ou à des fixtures mal configurées.
- **Fichier cible** : `tests/test_api/test_coaching.py`
- **Erreur principale** : Le mock de `redis_client` n'est pas correctement injecté dans les services sous-jacents (`CoachingLLMService`, `RedisVirtualFileSystem`) appelés par les endpoints FastAPI.
- **Environnement** : Docker (`conftest_docker.py` est utilisé via `TEST_PROFILE=docker`).

## 3. Objectifs Techniques
Réparer la suite de tests `test_coaching.py` pour qu'elle passe au vert (Green) sans modifier la logique métier de l'application.

### Tâches Requises :
1.  **Corriger l'Injection de Dépendance** :
    - S'assurer que `app.dependency_overrides[get_redis_client]` est correctement appliqué pour *toute* la durée du test.
    - Vérifier si `get_redis_vfs` (qui instancie `RedisVirtualFileSystem`) doit également être surchargé (mocké) pour éviter qu'il n'essaie de créer une vraie connexion Redis.
2.  **Nettoyer les Fixtures** :
    - Supprimer les redondances dans `test_coaching.py`.
    - S'assurer que le `mock_redis_client` simule correctement les méthodes `get`, `set`, `delete`, `exists` (async).
3.  **Vérification** :
    - Les tests doivent passer via la commande : `docker exec -e TEST_PROFILE=docker genesis-api pytest tests/test_api/test_coaching.py -vv`

## 4. Points d'Attention
- **Ne pas modifier `conftest_docker.py` ou `conftest_profile.py`** : Ces fichiers ont été stabilisés par le Tech Lead et fonctionnent pour les autres suites (`test_auth.py`, `test_business.py`). Le fix doit être localisé dans `test_coaching.py` ou via une surcharge spécifique.
- **LangGraph & LLM** : Si les tests appellent le LLM, s'assurer que `CoachingLLMService` est également mocké pour éviter des appels API externes (coûteux/lents).

## 5. Critères d'Acceptation (Definition of Done)
- [ ] La commande `pytest tests/test_api/test_coaching.py` retourne `PASSED` (100%).
- [ ] Aucun warning bloquant (Deprecation warnings Pydantic acceptables pour l'instant).
- [ ] Code de test propre et documenté.

---
**Note du Tech Lead** : "C'est une tâche de plomberie de test classique (Mocking/Dependency Injection). Fais en sorte que le CI soit vert. Merci."
