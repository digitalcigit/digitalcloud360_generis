# 📋 Work Order — GEN-10 : API Endpoints (Sites)

**Date :** 2025-12-05  
**De :** Tech Lead Genesis AI (Cascade)  
**À :** Développeur assigné  
**Objet :** Créer les endpoints API pour générer et récupérer des SiteDefinition

---

## 1. Contexte

GEN-10 est la **dernière pièce** qui connecte le Transformer backend (GEN-7) au Block Renderer frontend (GEN-9).

### Flux Complet

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   BusinessBrief │────▶│   Transformer   │────▶│  SiteDefinition │
│   (Existant)    │     │    (GEN-7 ✅)   │     │     JSON        │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                        ┌────────────────────────────────┘
                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   API Endpoint  │────▶│    Frontend     │────▶│   Site Visible  │
│   (GEN-10 🎯)   │     │    (GEN-9 ✅)   │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Liens de Suivi

| Outil | Lien / ID |
|-------|-----------|
| **Jira** | [GEN-10](https://digitalcloud360.atlassian.net/browse/GEN-10) |
| **Dépendances** | GEN-7 ✅, GEN-8 ✅, GEN-9 ✅ |

---

## 2. Environnement de Développement (Docker)

Le projet tourne sous Docker. Pour développer et tester les endpoints :

1.  **Lancer le backend :**
    ```bash
    cd c:\genesis
    docker-compose up -d genesis-api
    ```
2.  **Tester les endpoints :**
    ```bash
    # Via curl ou Postman sur http://localhost:8002/api/v1/sites/...
    ```
3.  **Exécuter les tests :**
    ```bash
    docker-compose exec genesis-api pytest tests/api/test_sites.py -v
    ```

---

## 3. Deadline & Estimation

| Métrique | Valeur |
|----------|--------|
| **Deadline** | **06/12/2025** |
| **Estimation** | 6-8h |
| **Priorité** | 🔴 Highest |

### 3.1 Non-Objectifs (Hors Scope GEN-10)

> ⚠️ **Ne PAS faire dans cette story :**

- ❌ Modifier le Transformer (GEN-7 terminé)
- ❌ Modifier les composants React (GEN-9 terminé)
- ❌ Implémenter la persistance DB (Redis suffit pour MVP)
- ❌ Authentification avancée (JWT existant suffit)
- ❌ Créer la page /preview frontend (scope GEN-11)

---

## 4. État Actuel du Code

### Endpoints existants : `app/api/v1/business.py`

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/brief/generate` | POST | Génère un BusinessBrief |
| `/brief/{brief_id}` | GET | Récupère un brief |
| `/brief/{brief_id}/results` | GET | Récupère résultats sub-agents |
| `/website/create` | POST | Crée site sur DC360 (legacy) |

### Transformer disponible : `app/services/transformer.py`

```python
from app.services.transformer import BriefToSiteTransformer

transformer = BriefToSiteTransformer()
site_definition = transformer.transform(business_brief)  # Dict validé Pydantic
```

---

## 5. Endpoints à Créer

### 5.1 Nouveau fichier : `app/api/v1/sites.py`

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/sites/generate` | POST | Génère un SiteDefinition depuis un brief_id |
| `/sites/{site_id}` | GET | Récupère un SiteDefinition existant |
| `/sites/{site_id}/preview` | GET | Retourne le SiteDefinition pour le renderer |

---

## 6. Spécifications Techniques

### 6.1 POST `/sites/generate`

**Input :**
```json
{
    "brief_id": "brief_550e8400-e29b-41d4-a716-446655440000"
}
```

**Output :**
```json
{
    "site_id": "site_123e4567-e89b-12d3-a456-426614174000",
    "brief_id": "brief_550e8400-e29b-41d4-a716-446655440000",
    "site_definition": {
        "metadata": { ... },
        "theme": { ... },
        "pages": [ ... ]
    },
    "created_at": "2025-12-05T14:30:00Z"
}
```

**Implémentation :**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.transformer import BriefToSiteTransformer
from app.core.integrations.redis_fs import RedisVirtualFileSystem
from app.api.v1.dependencies import get_redis_vfs, get_current_user
from app.models.coaching import BusinessBrief
import uuid
from datetime import datetime

router = APIRouter()
transformer = BriefToSiteTransformer()


@router.post(
    "/generate",
    status_code=status.HTTP_201_CREATED,
    summary="Générer un SiteDefinition depuis un BusinessBrief",
    description="""
    Transforme un BusinessBrief existant en SiteDefinition JSON
    utilisable par le Block Renderer frontend.
    
    **Workflow** :
    1. Charge le BusinessBrief depuis Redis (via brief_id)
    2. Applique le Transformer (mapping déterministe)
    3. Sauvegarde le SiteDefinition dans Redis
    4. Retourne le site_id et la définition complète
    """
)
async def generate_site(
    request: dict,
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    brief_id = request.get("brief_id")
    if not brief_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="`brief_id` is required."
        )
    
    # 1. Charger le brief depuis Redis
    brief_data = await redis_fs.read_session(current_user.id, brief_id)
    if not brief_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business brief not found."
        )
    
    # 2. Construire le BusinessBrief model
    # Adapter selon la structure réelle de brief_data
    business_brief = _build_business_brief_from_data(brief_data)
    
    # 3. Transformer en SiteDefinition
    site_definition = transformer.transform(business_brief)
    
    # 4. Sauvegarder dans Redis
    site_id = f"site_{uuid.uuid4()}"
    site_data = {
        "site_id": site_id,
        "brief_id": brief_id,
        "user_id": current_user.id,
        "site_definition": site_definition,
        "created_at": datetime.utcnow().isoformat()
    }
    await redis_fs.write_session(current_user.id, site_id, site_data)
    
    return site_data


def _build_business_brief_from_data(brief_data: dict) -> BusinessBrief:
    """
    Construit un BusinessBrief depuis les données Redis.
    À adapter selon la structure réelle.
    """
    results = brief_data.get("results", {})
    
    # Extraire les données du brief original ou des résultats
    return BusinessBrief(
        business_name=results.get("business_name", "Mon Entreprise"),
        sector=results.get("sector", "default"),
        mission=results.get("mission", ""),
        vision=results.get("vision", ""),
        value_proposition=results.get("value_proposition", ""),
        target_audience=results.get("target_audience", ""),
        differentiation=results.get("differentiation", ""),
        services=results.get("services", []),
        content_generation=results.get("content", {}),
        logo_creation=results.get("logo", {}),
        seo_optimization=results.get("seo", {}),
        template_selection=results.get("template", {})
    )
```

### 6.2 GET `/sites/{site_id}`

**Output :**
```json
{
    "site_id": "site_123e4567-e89b-12d3-a456-426614174000",
    "brief_id": "brief_550e8400...",
    "site_definition": { ... },
    "created_at": "2025-12-05T14:30:00Z"
}
```

**Implémentation :**

```python
@router.get(
    "/{site_id}",
    summary="Récupérer un SiteDefinition existant"
)
async def get_site(
    site_id: str,
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    site_data = await redis_fs.read_session(current_user.id, site_id)
    if not site_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found."
        )
    
    return site_data
```

### 6.3 GET `/sites/{site_id}/preview`

Endpoint optimisé pour le frontend qui retourne **uniquement** le `site_definition` (sans métadonnées).

```python
@router.get(
    "/{site_id}/preview",
    summary="Récupérer le SiteDefinition pour le renderer"
)
async def get_site_preview(
    site_id: str,
    current_user: dict = Depends(get_current_user),
    redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs)
):
    site_data = await redis_fs.read_session(current_user.id, site_id)
    if not site_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found."
        )
    
    # Retourne uniquement le site_definition pour le renderer
    return site_data.get("site_definition", {})
```

---

## 7. Enregistrement du Router

### Modifier `app/api/v1/__init__.py` ou `app/main.py`

```python
from app.api.v1.sites import router as sites_router

app.include_router(sites_router, prefix="/api/v1/sites", tags=["Sites"])
```

---

## 8. Tests Unitaires

### Créer `tests/api/test_sites.py`

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch


class TestSitesEndpoints:
    """Tests pour les endpoints /sites/*"""
    
    @pytest.fixture
    def mock_redis_fs(self):
        """Mock du Redis Virtual File System"""
        mock = AsyncMock()
        return mock
    
    @pytest.fixture
    def sample_brief_data(self):
        """Données de brief simulées"""
        return {
            "brief_id": "brief_test_123",
            "user_id": 1,
            "results": {
                "business_name": "TechStartup Dakar",
                "sector": "technology",
                "mission": "Digitaliser les PME",
                "vision": "Leader tech Afrique",
                "value_proposition": "Solutions sur mesure",
                "content": {
                    "hero_image": "https://example.com/hero.jpg"
                },
                "logo": {"logo_url": "https://example.com/logo.png"},
                "seo": {"keywords": ["tech", "dakar"]},
                "template": {"template_id": "tech-v2"}
            }
        }
    
    def test_generate_site_success(self, mock_redis_fs, sample_brief_data):
        """Test génération site avec brief valide"""
        mock_redis_fs.read_session.return_value = sample_brief_data
        mock_redis_fs.write_session.return_value = None
        
        # ... test implementation
        pass
    
    def test_generate_site_brief_not_found(self, mock_redis_fs):
        """Test erreur 404 si brief inexistant"""
        mock_redis_fs.read_session.return_value = None
        
        # ... test implementation
        pass
    
    def test_get_site_success(self, mock_redis_fs):
        """Test récupération site existant"""
        pass
    
    def test_get_site_not_found(self, mock_redis_fs):
        """Test erreur 404 si site inexistant"""
        pass
    
    def test_get_site_preview_returns_definition_only(self, mock_redis_fs):
        """Test que /preview retourne uniquement site_definition"""
        pass
```

---

## 9. Workflow Git

### 9.1 Créer ta branche

```bash
cd c:\genesis
git checkout master
git pull origin master
git checkout -b feature/gen-10-api-endpoints
```

### 9.2 Commits recommandés

```bash
git add app/api/v1/sites.py
git commit -m "feat(api): Add POST /sites/generate endpoint"

git add app/api/v1/sites.py
git commit -m "feat(api): Add GET /sites/{id} and /sites/{id}/preview endpoints"

git add tests/api/test_sites.py
git commit -m "test(api): Add unit tests for sites endpoints"

git add app/main.py  # ou __init__.py
git commit -m "feat(api): Register sites router"
```

### 9.3 Push et PR

```bash
git push origin feature/gen-10-api-endpoints
```

Créer une **Pull Request** vers `master` avec :
- Titre : `feat(api): [GEN-10] Add Sites API endpoints`
- Reviewer : Tech Lead Genesis (Cascade)

---

## 10. Critères d'Acceptation

- [ ] **POST `/sites/generate`** transforme un brief en SiteDefinition
- [ ] **GET `/sites/{site_id}`** retourne le site complet
- [ ] **GET `/sites/{site_id}/preview`** retourne uniquement le `site_definition`
- [ ] **Transformer** (GEN-7) est utilisé correctement
- [ ] **Redis** persiste les sites générés
- [ ] **Tests** passent (`pytest tests/api/test_sites.py`)
- [ ] **PR** créée et prête pour review

---

## 11. Ressources

| Document | Chemin |
|----------|--------|
| WO GEN-7 (Transformer) | `docs/memo/WO_GEN-7_TRANSFORMER_2025-12-04.md` |
| WO GEN-9 (Renderer) | `docs/memo/WO_GEN-9_BLOCK_RENDERER_2025-12-04.md` |
| Schema SiteDefinition | `app/schemas/site_definition.py` |
| Transformer | `app/services/transformer.py` |
| Endpoints Business | `app/api/v1/business.py` |

---

## 12. Contact

| Rôle | Contact |
|------|---------|
| Tech Lead | Cascade (review PR) |
| PO | À confirmer |

---

*— Tech Lead Genesis AI*
