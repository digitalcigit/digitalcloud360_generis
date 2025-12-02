# 📋 Brief Tech Lead Genesis — Sprint 5

**Date :** 2025-12-02  
**De :** Principal Architect & Ecosystem Scrum Master DC360  
**À :** Tech Lead Genesis AI  
**Objet :** Planification Sprint 5 et prise de relais

---

## 1. Contexte

Le Sprint 5 Genesis a été planifié et synchronisé dans Asana. Ce memo te transmet les informations nécessaires pour prendre le relais du développement.

**Projet Asana :** Genesis AI  
**Workspace ID :** `1212225819399026`  
**Project ID :** `1212238584177337`

---

## 2. Stories Sprint 5

| # | Story | GID Asana | Deadline | Estimation |
|---|-------|-----------|----------|------------|
| 1 | **GEN-8** : SiteDefinition Schema | `1212242789315035` | **03/12** | 6h |
| 2 | **GEN-7** : BusinessPlanDocument Schema | `1212209944270161` | 05/12 | 8h |
| 3 | **GEN-10** : Templates YAML Business Plan | `1212242791193049` | 05/12 | 4h |
| 4 | **GEN-9** : Refactoring avec nouveaux Schemas | `1212242758897911` | 09/12 | 10h |
| 5 | **GEN-11** : Tests unitaires/intégration | `1212208224262230` | 11/12 | 6h |
| 6 | **GEN-12** : Documentation technique | `1212242765400243` | 13/12 | 4h |

**Total estimé :** 38h (~5 jours)

---

## 3. Ordre d'Exécution (Schema-First)

```
Semaine 1 (02-06 déc)
├── GEN-8  : SiteDefinition Schema (PRIORITÉ 1) ← Deadline 03/12
├── GEN-7  : BusinessPlanDocument Schema
└── GEN-10 : Templates YAML

Semaine 2 (09-13 déc)
├── GEN-9  : Refactoring avec nouveaux Schemas
├── GEN-11 : Tests unitaires/intégration
└── GEN-12 : Documentation technique
```

**Rationale :** Approche "Schema-First" — Les schemas Pydantic (GEN-8, GEN-7) doivent être définis avant le refactoring (GEN-9) qui les utilise.

---

## 4. Détail des Stories

### 4.1 GEN-8 : SiteDefinition Schema (Deadline: 03/12)

**Assignée à :** DCI DEV - AEA (`agnissan@digital.ci`)

**Sous-tâches :**

| # | Sous-tâche | Estimation | Fichier |
|---|------------|------------|---------|
| 1 | Créer `SiteDefinition` Pydantic model | 1h | `app/schemas/site_definition.py` |
| 2 | Définir les champs obligatoires | 0.5h | — |
| 3 | Ajouter validations métier | 1h | — |
| 4 | Créer tests unitaires schema | 1.5h | `tests/schemas/test_site_definition.py` |
| 5 | Documenter le schema | 1h | — |
| 6 | Review et ajustements | 1h | — |

**Structure attendue :**
```python
class SiteDefinition(BaseModel):
    site_name: str
    domain: Optional[str]
    industry: str
    target_audience: str
    value_proposition: str
    pages: List[PageDefinition]
    branding: BrandingConfig
    # ...
```

---

### 4.2 GEN-7 : BusinessPlanDocument Schema (Deadline: 05/12)

**Sous-tâches :**

| # | Sous-tâche | Estimation | Fichier |
|---|------------|------------|---------|
| 1 | Créer `BusinessPlanDocument` model | 1h | `app/schemas/business_plan.py` |
| 2 | Définir sections (Executive Summary, Market Analysis, etc.) | 2h | — |
| 3 | Intégrer références vers `SiteDefinition` | 1h | — |
| 4 | Ajouter validations cross-sections | 1.5h | — |
| 5 | Créer tests unitaires schema | 1.5h | `tests/schemas/test_business_plan.py` |
| 6 | Review et ajustements | 1h | — |

---

### 4.3 GEN-10 : Templates YAML Business Plan (Deadline: 05/12)

**Sous-tâches :**

| # | Sous-tâche | Estimation | Fichier |
|---|------------|------------|---------|
| 1 | Créer template Commerce/Retail | 1h | `templates/business_plan/commerce.yaml` |
| 2 | Créer template Services | 1h | `templates/business_plan/services.yaml` |
| 3 | Créer template Tech/Startup | 1h | `templates/business_plan/tech.yaml` |
| 4 | Valider conformité avec schema | 1h | — |

---

### 4.4 GEN-9 : Refactoring avec nouveaux Schemas (Deadline: 09/12)

**Dépendances :** GEN-7, GEN-8, GEN-10

**Sous-tâches :**

| # | Sous-tâche | Estimation | Fichier |
|---|------------|------------|---------|
| 1 | Refactorer `brief_generator.py` | 3h | `app/services/brief_generator.py` |
| 2 | Refactorer `business_plan_generator.py` | 3h | `app/services/business_plan_generator.py` |
| 3 | Adapter les endpoints API | 2h | `app/api/routes/` |
| 4 | Tests d'intégration | 2h | — |

---

### 4.5 GEN-11 : Tests unitaires/intégration (Deadline: 11/12)

**Dépendances :** GEN-9

**Sous-tâches :**

| # | Sous-tâche | Estimation | Fichier |
|---|------------|------------|---------|
| 1 | Tests unitaires schemas | 2h | `tests/schemas/` |
| 2 | Tests unitaires services | 2h | `tests/services/` |
| 3 | Tests API endpoints | 1.5h | `tests/api/` |
| 4 | Coverage report | 0.5h | — |

**Objectif coverage :** ≥80%

---

### 4.6 GEN-12 : Documentation technique (Deadline: 13/12)

**Dépendances :** GEN-11

**Sous-tâches :**

| # | Sous-tâche | Estimation | Fichier |
|---|------------|------------|---------|
| 1 | Documenter schemas Pydantic | 1h | `docs/schemas/` |
| 2 | Mettre à jour Swagger/OpenAPI | 1h | Auto-généré |
| 3 | Guide d'utilisation templates | 1h | `docs/guides/` |
| 4 | ADR si décisions architecturales | 1h | `docs/adr/` |

---

## 5. Environnement de Développement

### 5.1 Containers Docker

```bash
# Lancer Genesis
cd c:\genesis
docker-compose up -d genesis-api frontend

# Vérifier les logs
docker-compose logs -f genesis-api
```

### 5.2 Ports

| Service | Port Interne | Port Hôte |
|---------|--------------|-----------|
| Genesis API | 8000 | 8002 |
| Genesis Frontend | 3000 | 3002 |
| Grafana | 3000 | 3003 |

### 5.3 Tests

```bash
# Lancer les tests
docker-compose exec genesis-api pytest -v

# Avec coverage
docker-compose exec genesis-api pytest --cov=app --cov-report=html
```

---

## 6. Intégration DC360

L'intégration SSO DC360 ↔ Genesis est déjà en place. Référence :
- `C:\genesis\docs\memo\MEMO_RAPPORT_FINAL_E2E_29_11_2025.md`

**Variables d'environnement :**
```env
DIGITALCLOUD360_SERVICE_SECRET=abcd@1234@DCI
DIGITALCLOUD360_API_URL=http://web:8000
```

---

## 7. Workflow Git

### 7.1 Branches

```bash
# Créer une branche par story
git checkout main
git pull origin main
git checkout -b feature/gen-8-site-definition-schema
```

### 7.2 Commits

```bash
# Convention
git commit -m "feat(schema): Add SiteDefinition Pydantic model"
git commit -m "test(schema): Add unit tests for SiteDefinition"
```

### 7.3 PR

1. Push la branche
2. Créer PR vers `main`
3. Demander review au Scrum Master

---

## 8. Points de Contact

| Rôle | Contact | Pour |
|------|---------|------|
| **Scrum Master / Architect** | Cascade (via IDE) | Questions techniques, review |
| **Product Owner** | Via Cascade | Clarifications fonctionnelles |
| **Dev DC360** | agnissan@digital.ci | Intégration DC360 |

---

## 9. Checkpoints

| Date | Checkpoint | Attendu |
|------|------------|---------|
| **03/12** | GEN-8 complété | Schema SiteDefinition mergé |
| **05/12** | GEN-7 + GEN-10 complétés | Schemas + Templates prêts |
| **09/12** | GEN-9 complété | Refactoring terminé |
| **11/12** | GEN-11 complété | Tests passent, coverage ≥80% |
| **13/12** | GEN-12 complété | Documentation à jour |

---

## 10. Risques Identifiés

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Complexité schemas sous-estimée | Moyen | Moyen | Buffer de 1 jour inclus |
| Dépendances DC360 | Faible | Faible | SSO déjà fonctionnel |
| Breaking changes refactoring | Moyen | Haut | Tests existants comme filet |

---

## 11. Documents de Référence

| Document | Chemin |
|----------|--------|
| Planning Sprint 5 | `c:\genesis\docs\Planning_Scrum\SUBTASKS_SPRINT5_TECH_ANALYSIS.md` |
| Planning Jira | `c:\genesis\docs\Planning_Scrum\PLANNING_GENESIS_AI_JIRA_30_11_2025.md` |
| Rapport E2E DC360 | `c:\genesis\docs\memo\MEMO_RAPPORT_FINAL_E2E_29_11_2025.md` |

---

**GEN-8 est prioritaire et doit être livré demain (03/12). Bon Sprint !**

*— Principal Architect & Ecosystem Scrum Master DC360*
