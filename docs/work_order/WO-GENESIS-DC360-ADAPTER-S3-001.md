---
title: "Work Order - Endpoint Alias DC360 + Adaptateur Payload"
code: "WO-GENESIS-DC360-ADAPTER-S3-001"
priority: "HAUTE - BLOQUANT"
assignee: "Senior Developer Genesis"
reviewer: "Tech Lead Genesis (Cascade)"
date: "2025-11-26"
sprint: "Sprint 3 - Intégration DC360"
estimated_effort: "2h30"
tags: ["api", "integration", "dc360", "adapter", "fastapi"]
status: "completed"
completion_date: "2025-11-26"
merge_commit: "572c43c4"
---

# 🎯 WORK ORDER : Endpoint Alias DC360 + Adaptateur

## Contexte

Le frontend DigitalCloud360 est **bloqué** sur un 404 lors de l'appel à l'endpoint de génération de brief. La cause : désalignement entre le path appelé par DC360 et le path exposé par Genesis.

### Décision technique (validée)

| Document | Référence |
|----------|-----------|
| Demande DC360 | `MEMO_TECH_LEAD_GENESIS_DC360_INTEGRATION_2025-11-26.md` |
| Réponse Genesis | `MEMO_RESPONSE_TECH_LEAD_GENESIS_DC360_INTEGRATION_2025-11-26.md` |
| Validation DC360 | `MEMO_DC360_REPONSE_ALIGNEMENT_API_2025-11-26.md` |

**Option retenue : Option B - Alias + Adaptateur côté Genesis**

---

## 1️⃣ OBJECTIF

Créer un endpoint alias `/api/genesis/generate-brief/` qui :
1. Accepte le payload format DC360
2. Adapte vers le schéma Genesis interne
3. Appelle l'orchestrateur LangGraph existant
4. Retourne la réponse au format Genesis (DC360 s'adapte côté frontend)

---

## 2️⃣ SPÉCIFICATIONS TECHNIQUES

### 2.1 Endpoint à créer

```
POST /api/genesis/generate-brief/
```

**Note :** Sans le préfixe `/v1/` - c'est un alias dédié DC360.

### 2.2 Authentification

- **Header requis :** `X-Service-Secret`
- **Valeur :** Doit correspondre à `settings.GENESIS_SERVICE_SECRET`
- **Erreur si absent/invalide :** 401 Unauthorized

### 2.3 Payload entrant (format DC360)

```json
{
  "user_id": 123,
  "business_info": {
    "company_name": "Ma Startup",
    "industry": "Tech",
    "company_size": "1-10",
    "description": "Une startup innovante dans la tech au Sénégal"
  },
  "market_info": {
    "target_audience": "PME et entrepreneurs",
    "competitors": ["Competitor A", "Competitor B"],
    "market_challenges": "Accès au financement, digitalisation",
    "goals": ["Augmenter visibilité", "Générer des leads"]
  }
}
```

### 2.4 Mapping Payload DC360 → Genesis

| Champ DC360 | Champ Genesis | Transformation |
|-------------|---------------|----------------|
| `user_id` | `user_id` | Direct |
| `business_info.company_name` | `brief_data.business_name` | Direct |
| `business_info.industry` | `brief_data.industry_sector` | Direct |
| `business_info.company_size` | - | Ignoré (non utilisé par Genesis) |
| `business_info.description` | `brief_data.vision` | Direct |
| `business_info.description` | `brief_data.mission` | Copie (même valeur) |
| `market_info.target_audience` | `brief_data.target_market` | Direct |
| `market_info.competitors` | `brief_data.competitive_advantage` | Join avec virgules |
| `market_info.goals` | `brief_data.services` | Direct (liste) |
| - | `brief_data.location` | Défaut: `{"country": "Sénégal", "city": "Dakar", "region": "Afrique de l'Ouest"}` |
| - | `coaching_session_id` | Auto-généré: `session_{uuid[:8]}` |

### 2.5 Réponse (format Genesis conservé)

```json
{
  "id": "brief_a1b2c3d4e5f6",
  "user_id": 123,
  "session_id": "session_abc12345",
  "status": "completed",
  "market_research": {
    "status": "completed",
    "data": { ... },
    "timestamp": "2025-11-26T01:30:00Z"
  },
  "content_generation": {
    "status": "completed",
    "data": { ... },
    "timestamp": "2025-11-26T01:30:00Z"
  },
  "logo_creation": {
    "status": "completed",
    "data": { ... },
    "timestamp": "2025-11-26T01:30:00Z"
  },
  "seo_optimization": {
    "status": "completed",
    "data": { ... },
    "timestamp": "2025-11-26T01:30:00Z"
  },
  "template_selection": {
    "status": "completed",
    "data": { ... },
    "timestamp": "2025-11-26T01:30:00Z"
  },
  "overall_confidence": 0.85,
  "is_ready_for_website": true,
  "generated_at": "2025-11-26T01:30:00Z",
  "tokens_used": 1250
}
```

---

## 3️⃣ FICHIERS À CRÉER/MODIFIER

### 3.1 Nouveau fichier : `app/api/dc360_adapter.py`

Ce fichier contient :

1. **Schémas Pydantic DC360** :
   - `DC360BusinessInfo`
   - `DC360MarketInfo`
   - `DC360GenerateBriefRequest`
   - `DC360GenerateBriefResponse`

2. **Fonction de validation service secret** :
   ```python
   async def verify_service_secret(
       x_service_secret: str = Header(..., alias="X-Service-Secret")
   ) -> bool:
       if x_service_secret != settings.GENESIS_SERVICE_SECRET:
           raise HTTPException(status_code=401, detail="Invalid service secret")
       return True
   ```

3. **Fonction adaptateur payload** :
   ```python
   def adapt_dc360_to_genesis(dc360_request: DC360GenerateBriefRequest) -> dict:
       """Transforme le payload DC360 vers le format Genesis interne."""
       # Implémentation du mapping ci-dessus
   ```

4. **Endpoint principal** :
   ```python
   @router.post("/generate-brief/", response_model=DC360GenerateBriefResponse, status_code=201)
   async def generate_brief_dc360(
       request: DC360GenerateBriefRequest,
       _: bool = Depends(verify_service_secret),
       orchestrator: LangGraphOrchestrator = Depends(get_orchestrator),
       redis_fs: RedisVirtualFileSystem = Depends(get_redis_vfs),
       quota_manager: QuotaManager = Depends(get_quota_manager)
   ):
       # 1. Vérifier quota
       # 2. Adapter payload
       # 3. Appeler orchestrateur
       # 4. Sauvegarder Redis
       # 5. Retourner réponse
   ```

### 3.2 Modifier : `app/main.py`

Ajouter le nouveau router **SANS** le préfixe `/v1/` :

```python
from app.api import dc360_adapter

# Après les autres routers
app.include_router(
    dc360_adapter.router,
    prefix="/api/genesis",  # PAS de /v1/
    tags=["DC360 Integration"]
)
```

---

## 4️⃣ GESTION DES ERREURS

| Code | Condition | Response |
|------|-----------|----------|
| 201 | Succès | Brief généré |
| 400 | Payload invalide | `{"error": "INVALID_PAYLOAD", "message": "..."}` |
| 401 | X-Service-Secret manquant/invalide | `{"error": "UNAUTHORIZED", "message": "Invalid service secret"}` |
| 403 | Quota dépassé | `{"error": "QUOTA_EXCEEDED", "message": "...", "quota_info": {...}}` |
| 500 | Erreur orchestration | `{"error": "GENERATION_FAILED", "message": "..."}` |
| 504 | Timeout (>65s) | `{"error": "TIMEOUT", "message": "Generation timeout"}` |

---

## 5️⃣ TESTS REQUIS

### 5.1 Test unitaire adaptateur

Fichier : `tests/test_dc360_adapter.py`

```python
def test_adapt_dc360_to_genesis():
    """Vérifie la transformation du payload DC360 → Genesis."""
    dc360_payload = {
        "user_id": 123,
        "business_info": {
            "company_name": "Test Corp",
            "industry": "Tech",
            "description": "Test description"
        },
        "market_info": {
            "target_audience": "PME",
            "competitors": ["A", "B"],
            "goals": ["Goal 1"]
        }
    }
    
    genesis_payload = adapt_dc360_to_genesis(dc360_payload)
    
    assert genesis_payload["user_id"] == 123
    assert genesis_payload["brief_data"]["business_name"] == "Test Corp"
    assert genesis_payload["brief_data"]["industry_sector"] == "Tech"
    assert genesis_payload["brief_data"]["target_market"] == "PME"
    assert "session_" in genesis_payload.get("coaching_session_id", "")
```

### 5.2 Test endpoint

```python
@pytest.mark.asyncio
async def test_generate_brief_dc360_endpoint():
    """Test E2E de l'endpoint alias DC360."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/genesis/generate-brief/",
            json={...},
            headers={"X-Service-Secret": "test_secret"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "completed"
```

### 5.3 Test erreur 401

```python
async def test_generate_brief_missing_secret():
    """Test refus sans X-Service-Secret."""
    response = await client.post("/api/genesis/generate-brief/", json={...})
    assert response.status_code == 401
```

---

## 6️⃣ DEFINITION OF DONE (DoD)

- [ ] Fichier `app/api/dc360_adapter.py` créé avec schémas et endpoint
- [ ] Router monté dans `app/main.py` sur `/api/genesis`
- [ ] Validation `X-Service-Secret` fonctionnelle
- [ ] Adaptateur payload DC360 → Genesis implémenté
- [ ] Quota check avant génération
- [ ] Persistance Redis post-génération
- [ ] Tests unitaires passants (≥3 tests)
- [ ] Endpoint accessible sur `POST /api/genesis/generate-brief/`
- [ ] Documentation OpenAPI visible sur `/docs`
- [ ] Code review par Tech Lead

---

## 7️⃣ RÉFÉRENCES

- **Schémas Genesis existants :** `app/api/v1/genesis.py` lignes 36-107
- **Orchestrateur :** `app/core/orchestration/langgraph_orchestrator.py`
- **Redis VFS :** `app/core/integrations/redis_fs.py`
- **Quota Manager :** `app/core/quota.py`
- **Settings :** `app/config/settings.py`

---

## 📞 SUPPORT

Pour toute question ou blocage :
- **Tech Lead Genesis :** Cascade
- **Canal :** Memo dans `docs/memo/`

---

**Bonne implémentation !**
