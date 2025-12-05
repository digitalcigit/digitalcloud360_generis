# 🔥 Work Order HOTFIX — Brief Generate 500 Error

**Date :** 2025-12-05  
**De :** Tech Lead Genesis AI (Cascade)  
**À :** Développeur assigné  
**Priorité :** 🔴 HAUTE (bloque le test E2E Phase 1B)  
**Objet :** Corriger INTERNAL_SERVER_ERROR sur `POST /api/v1/business/brief/generate`

---

## 1. Contexte

Lors du test E2E de la Phase 1B (flux Brief → Site → Preview), l'appel à l'endpoint de génération de brief renvoie une erreur 500 :

```json
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "Une erreur inattendue s'est produite"
}
```

### Diagnostic

Après analyse des logs Docker (`genesis-api`), la **cause racine** est identifiée :

```python
{'type': 'missing', 'loc': ('response', 'created_at'), 'msg': 'Field required', ...}
```

**Le brief est généré avec succès** par l'orchestrateur (market_research, content_generation, template_selection, etc.), mais la **validation Pydantic de la réponse** échoue car le champ `created_at` est requis dans `BusinessBriefResponse` mais absent de la réponse construite.

---

## 2. Objectif

Corriger l'endpoint `POST /api/v1/business/brief/generate` pour qu'il renvoie une réponse valide selon le schéma `BusinessBriefResponse`.

### Non-Objectifs

- ❌ Modifier l'orchestrateur LangGraph
- ❌ Modifier les sub-agents
- ❌ Modifier le Transformer (GEN-7)
- ❌ Modifier les endpoints sites (GEN-10)

---

## 3. Fichiers Concernés

| Fichier | Action |
|---------|--------|
| `app/api/v1/business.py` | Ajouter `created_at` dans la réponse |
| `app/schemas/business.py` | Optionnel : rendre `created_at` optionnel si pertinent |
| `tests/api/test_business.py` | Ajouter/mettre à jour le test de `brief/generate` |

---

## 4. Analyse du Code Actuel

### 4.1 Schéma de Réponse (`app/schemas/business.py`)

```python
class BusinessBriefResponse(BaseModel):
    """Réponse avec brief business complet"""
    id: int
    coaching_session_id: int
    business_brief: BusinessBrief
    market_research: Optional[Dict[str, Any]] = None
    content_generation: Optional[Dict[str, Any]] = None
    logo_creation: Optional[Dict[str, Any]] = None
    seo_optimization: Optional[Dict[str, Any]] = None
    template_selection: Optional[Dict[str, Any]] = None
    overall_confidence: float
    is_ready_for_website: bool
    created_at: datetime  # ⚠️ REQUIS mais absent de la réponse
    
    class Config:
        from_attributes = True
```

### 4.2 Problème

L'endpoint `brief/generate` (dans `app/api/v1/business.py` ou `genesis.py`) construit une réponse qui ne contient pas le champ `created_at`, provoquant l'échec de validation Pydantic.

---

## 5. Solution Recommandée

### Option A : Ajouter `created_at` dans la réponse (RECOMMANDÉ)

Dans l'endpoint `brief/generate`, ajouter le timestamp lors de la construction de la réponse :

```python
from datetime import datetime

# Dans la construction de la réponse
response_data = {
    "id": brief_id,  # ou un ID généré
    "coaching_session_id": request.coaching_session_id,
    "business_brief": brief_data.get("business_brief", {}),
    "market_research": brief_data.get("market_research"),
    "content_generation": brief_data.get("content_generation"),
    "logo_creation": brief_data.get("logo_creation"),
    "seo_optimization": brief_data.get("seo_optimization"),
    "template_selection": brief_data.get("template_selection"),
    "overall_confidence": brief_data.get("overall_confidence", 0.5),
    "is_ready_for_website": brief_data.get("is_ready_for_website", False),
    "created_at": datetime.utcnow(),  # ✅ AJOUTER CETTE LIGNE
}
```

### Option B : Rendre `created_at` optionnel (Alternative)

Si `created_at` n'est pas toujours pertinent pour les briefs Redis (non persistés en DB) :

```python
# app/schemas/business.py
class BusinessBriefResponse(BaseModel):
    # ...
    created_at: Optional[datetime] = None  # Rendre optionnel
```

---

## 6. Tests Requis

### 6.1 Test Unitaire (`tests/api/test_business.py`)

```python
import pytest
from httpx import AsyncClient

class TestBusinessBriefGenerate:
    """Tests pour POST /api/v1/business/brief/generate"""

    async def test_generate_brief_success(self, client: AsyncClient, auth_headers: dict):
        """Test génération de brief réussie."""
        request_data = {
            "coaching_session_id": 789,
            "session_id": "session_test_123",
            "business_brief": {
                "business_name": "TechStartup Dakar",
                "vision": "Devenir leader tech",
                "mission": "Démocratiser l'accès digital",
                "target_audience": "PME",
                "differentiation": "Support local",
                "value_proposition": "Solutions abordables",
                "sector": "Technology",
                "location": {"city": "Dakar", "country": "Senegal", "region": "West Africa"}
            }
        }
        
        response = await client.post(
            "/api/v1/business/brief/generate",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier les champs requis
        assert "id" in data or "brief_id" in data
        assert "business_brief" in data
        assert "overall_confidence" in data
        assert "is_ready_for_website" in data
        # ✅ Vérifier created_at si Option A
        # assert "created_at" in data
```

---

## 7. Workflow Git

```bash
# 1. Créer la branche
git checkout master
git pull origin master
git checkout -b hotfix/brief-generate-created-at

# 2. Appliquer le fix
# ... éditer les fichiers ...

# 3. Tester localement
docker-compose exec genesis-api pytest tests/api/test_business.py -v

# 4. Commit
git add .
git commit -m "fix(api): Add created_at to brief/generate response"

# 5. Push et PR
git push origin hotfix/brief-generate-created-at
```

---

## 8. Critères d'Acceptation

| # | Critère | Validation |
|---|---------|------------|
| 1 | `POST /api/v1/business/brief/generate` renvoie 200 | ✅ |
| 2 | La réponse contient tous les champs requis par `BusinessBriefResponse` | ✅ |
| 3 | Le test E2E (brief → site → preview) passe | ✅ |
| 4 | Tests unitaires ajoutés/mis à jour | ✅ |

---

## 9. Estimation

| Tâche | Temps |
|-------|-------|
| Diagnostic (déjà fait) | ✅ |
| Fix endpoint | 30 min |
| Test unitaire | 30 min |
| Test E2E manuel | 15 min |
| PR + Review | 15 min |
| **Total** | **~1h30** |

---

## 10. Ressources

- **Logs Docker** : `docker logs genesis-api --tail 500 2>&1 | Select-String "error|brief"`
- **Schema** : `app/schemas/business.py` → `BusinessBriefResponse`
- **Endpoint** : `app/api/v1/business.py` ou `app/api/v1/genesis.py`

---

## 11. Contact

- **Tech Lead** : Cascade (via chat)
- **Asana** : À créer (GEN-HOTFIX-BRIEF)

---

*Ce hotfix est bloquant pour le test E2E Phase 1B. Priorité haute.*
