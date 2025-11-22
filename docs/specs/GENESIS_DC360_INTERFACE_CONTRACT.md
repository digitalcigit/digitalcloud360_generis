---
TITRE: Contrat d'Interface Genesis AI ↔ DigitalCloud360
VERSION: 1.0.0
DATE: 2025-11-22
AUTEURS: Tech Lead Genesis AI (agnissaneric), Tech Lead DC360
STATUT: 🟢 ACTIF - Phase 2 Sprint 3
---

# CONTRAT D'INTERFACE GENESIS AI ↔ DIGITALCLOUD360

## 1. VUE D'ENSEMBLE

### 1.1 Objectif
Définir les spécifications techniques exactes pour l'intégration bidirectionnelle entre **Genesis AI** (service de génération de business briefs) et **DigitalCloud360** (plateforme de création de sites web).

### 1.2 Architecture
```
┌─────────────────┐         ┌──────────────────┐
│  DC360 Frontend │────────▶│  DC360 Backend   │
│   (Wizard UI)   │         │   (Proxy/Direct) │
└─────────────────┘         └──────────────────┘
                                     │
                                     │ HTTP/REST
                                     │ X-Service-Secret
                                     │
                                     ▼
                            ┌──────────────────┐
                            │   GENESIS AI     │
                            │   (Service)      │
                            └──────────────────┘
                                     │
                                     │ Providers
                                     ▼
                            [ Kimi, Deepseek, Redis ]
```

### 1.3 Flux de données principal
1. **DC360 → Genesis** : Vérification quotas utilisateur
2. **DC360 → Genesis** : Requête génération business brief
3. **Genesis → DC360** : Brief généré (JSON structuré)
4. **DC360 → Genesis** : Récupération brief par ID
5. **DC360** : Création site web depuis brief

---

## 2. ENDPOINTS GENESIS AI (Exposés pour DC360)

### 2.1 URL Base & Documentation

**Environnements** :
- **Local Dev** : `http://localhost:8000`
- **Staging** : `https://genesis-staging.digitalcloud360.com` (à venir)
- **Production** : `https://genesis.digitalcloud360.com` (à venir)

**Documentation Interactive** :
- **Swagger UI** : `{BASE_URL}/docs`
- **ReDoc** : `{BASE_URL}/redoc`
- **OpenAPI JSON** : `{BASE_URL}/openapi.json`

**Exemple local** : http://localhost:8000/docs

---

### 2.2 Authentification Inter-services

**Méthode** : Header HTTP personnalisé

**Header requis** :
```http
X-Service-Secret: <SECRET_PARTAGÉ>
```

**Configuration** :
```bash
# Dans .env de Genesis AI
GENESIS_SERVICE_SECRET=your-secret-here-min-32-chars

# Dans .env de DC360
DIGITALCLOUD360_SERVICE_SECRET=your-secret-here-min-32-chars
```

**⚠️ IMPORTANT** : Les deux secrets doivent être identiques !

**Codes erreur** :
- `401 Unauthorized` : Header manquant ou secret invalide
- `403 Forbidden` : Service non autorisé

---

### 2.3 Endpoint : GET /api/v1/business-brief/{id}

**Description** : Récupère un business brief complet généré par Genesis AI.

**URL** : `GET /api/v1/business-brief/{brief_id}`

**Headers** :
```http
X-Service-Secret: <SECRET>
Content-Type: application/json
```

**Path Parameters** :
| Param | Type | Requis | Description |
|-------|------|--------|-------------|
| `brief_id` | string | ✅ | UUID du brief (format: `uuid4`) |

**Réponse Succès (200 OK)** :

```json
{
  "brief_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": 42,
  "coaching_session_id": "session_abc123",
  "business_name": "TechHub Dakar",
  "vision": "Devenir la référence de l'innovation technologique en Afrique de l'Ouest d'ici 2030",
  "mission": "Démocratiser l'accès aux solutions tech pour les PME sénégalaises",
  "target_audience": "PME et entrepreneurs au Sénégal, 25-45 ans, secteur tertiaire",
  "differentiation": "Support client en wolof et français, paiement mobile intégré",
  "sector": "Technology",
  "location": {
    "city": "Dakar",
    "country": "Sénégal",
    "region": "Afrique de l'Ouest"
  },
  "results": {
    "research": {
      "market_analysis": {
        "market_size": "Le marché sénégalais du numérique représente 450M€ en 2024, avec une croissance de 12% annuelle.",
        "trends": [
          "Digitalisation accélérée post-COVID",
          "Adoption croissante du mobile money",
          "Essor des startups tech à Dakar"
        ],
        "target_demographics": {
          "age_range": "25-45 ans",
          "income_level": "Classe moyenne et moyenne supérieure",
          "tech_adoption": "Taux de pénétration smartphone 78%"
        }
      },
      "competitors": [
        {
          "name": "Jokkolabs",
          "strengths": "Réseau établi, incubateur reconnu",
          "weaknesses": "Moins axé sur services directs aux PME",
          "market_position": "Leader incubation"
        },
        {
          "name": "Teranga Tech",
          "strengths": "Formation tech de qualité",
          "weaknesses": "Pas d'accompagnement business complet",
          "market_position": "Challenger formation"
        }
      ],
      "opportunities": [
        {
          "description": "Programme gouvernemental Digital Sénégal 2025",
          "potential": "Subventions et appels à projets disponibles",
          "timeline": "2025-2027"
        },
        {
          "description": "Partenariat avec opérateurs télécoms",
          "potential": "Distribution via réseaux Orange/Free",
          "timeline": "Court terme (6 mois)"
        }
      ]
    },
    "content": {
      "homepage": {
        "fr": {
          "hero_title": "Transformez votre entreprise avec la tech",
          "hero_subtitle": "Solutions digitales accessibles pour PME sénégalaises",
          "cta_primary": "Démarrer maintenant",
          "value_propositions": [
            "Support en français et wolof",
            "Paiement mobile intégré",
            "Accompagnement personnalisé"
          ]
        }
      },
      "about": {
        "fr": {
          "story": "TechHub Dakar est né de la conviction que chaque entrepreneur mérite...",
          "mission_statement": "Notre mission est de démocratiser l'accès aux technologies...",
          "values": [
            "Innovation accessible",
            "Excellence locale",
            "Impact communautaire"
          ]
        }
      },
      "services": {
        "fr": {
          "list": [
            {
              "name": "Conseil Digital",
              "description": "Audit et stratégie digitale sur mesure",
              "pricing": "À partir de 150 000 FCFA"
            },
            {
              "name": "Solutions Tech",
              "description": "Développement d'applications web et mobile",
              "pricing": "Sur devis"
            },
            {
              "name": "Formation",
              "description": "Formation des équipes aux outils digitaux",
              "pricing": "75 000 FCFA/jour"
            }
          ]
        }
      },
      "contact": {
        "fr": {
          "address": "Plateau, Dakar, Sénégal",
          "phone": "+221 33 XXX XX XX",
          "email": "contact@techhub-dakar.sn",
          "hours": "Lun-Ven: 9h-18h, Sam: 9h-13h"
        }
      }
    },
    "logo": {
      "url": "https://example.com/logos/techhub-dakar-logo.png",
      "style": "modern_tech",
      "colors": {
        "primary": "#1E40AF",
        "secondary": "#FBBF24",
        "accent": "#10B981"
      }
    },
    "seo": {
      "meta_title": "TechHub Dakar - Solutions Digitales PME Sénégal",
      "meta_description": "Transformez votre entreprise avec nos solutions tech accessibles. Support français/wolof, paiement mobile, accompagnement personnalisé.",
      "keywords": [
        "solutions digitales Sénégal",
        "PME tech Dakar",
        "transformation digitale Afrique",
        "accompagnement numérique"
      ],
      "og_image": "https://example.com/og/techhub-social.jpg"
    },
    "template": {
      "id": "modern_business_01",
      "name": "Modern Business",
      "category": "business",
      "features": [
        "responsive",
        "dark_mode",
        "animations",
        "contact_form"
      ]
    }
  },
  "metadata": {
    "confidence_score": 0.85,
    "ready_for_website": true,
    "generation_time_seconds": 54.3,
    "providers_used": {
      "search": "kimi",
      "llm": "deepseek",
      "image": "dalle-3"
    },
    "languages_available": ["fr"],
    "successful_agents": ["research", "content", "template"],
    "failed_agents": ["logo", "seo"]
  },
  "timestamps": {
    "created_at": "2025-11-22T20:05:04Z",
    "updated_at": "2025-11-22T20:05:58Z",
    "expires_at": "2025-11-29T20:05:58Z"
  }
}
```

**Réponses Erreur** :

```json
// 401 Unauthorized
{
  "detail": "Not authenticated",
  "error": "UNAUTHORIZED"
}

// 403 Forbidden
{
  "detail": "Service not authorized",
  "error": "FORBIDDEN"
}

// 404 Not Found
{
  "detail": "Business brief not found",
  "error": "NOT_FOUND",
  "brief_id": "invalid-id-123"
}

// 500 Internal Server Error
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "Une erreur inattendue s'est produite",
  "timestamp": 1732298701.206899
}
```

**Codes HTTP** :
- `200 OK` : Brief récupéré avec succès
- `401 Unauthorized` : Authentification manquante/invalide
- `403 Forbidden` : Service non autorisé
- `404 Not Found` : Brief inexistant ou expiré (TTL Redis)
- `500 Internal Server Error` : Erreur serveur

---

### 2.4 Endpoint : GET /api/v1/business-brief/user/{user_id}

**Description** : Liste tous les business briefs d'un utilisateur.

**URL** : `GET /api/v1/business-brief/user/{user_id}`

**Headers** :
```http
X-Service-Secret: <SECRET>
Content-Type: application/json
```

**Path Parameters** :
| Param | Type | Requis | Description |
|-------|------|--------|-------------|
| `user_id` | integer | ✅ | ID utilisateur DC360 |

**Query Parameters** :
| Param | Type | Défaut | Description |
|-------|------|--------|-------------|
| `limit` | integer | 10 | Nombre max de briefs (1-100) |
| `offset` | integer | 0 | Pagination offset |
| `sort` | string | `created_desc` | Tri (`created_desc`, `created_asc`) |

**Exemple** : `GET /api/v1/business-brief/user/42?limit=5&offset=0&sort=created_desc`

**Réponse Succès (200 OK)** :

```json
{
  "user_id": 42,
  "total_count": 12,
  "briefs": [
    {
      "brief_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "business_name": "TechHub Dakar",
      "sector": "Technology",
      "location": {
        "city": "Dakar",
        "country": "Sénégal"
      },
      "created_at": "2025-11-22T20:05:04Z",
      "confidence_score": 0.85,
      "ready_for_website": true
    },
    {
      "brief_id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
      "business_name": "Café Teranga",
      "sector": "Restaurant",
      "location": {
        "city": "Dakar",
        "country": "Sénégal"
      },
      "created_at": "2025-11-21T15:30:22Z",
      "confidence_score": 0.78,
      "ready_for_website": true
    }
  ],
  "pagination": {
    "limit": 5,
    "offset": 0,
    "has_more": true
  }
}
```

**Codes HTTP** :
- `200 OK` : Liste récupérée (peut être vide `[]`)
- `401 Unauthorized` : Authentification manquante/invalide
- `403 Forbidden` : Service non autorisé
- `500 Internal Server Error` : Erreur serveur

---

## 3. ENDPOINTS DC360 (Requis par Genesis)

### 3.1 Endpoint : GET /api/users/{id}/subscription

**Description** : Retourne les informations d'abonnement Genesis AI d'un utilisateur DC360.

**URL** : `GET /api/users/{user_id}/subscription`

**Headers** :
```http
X-Service-Secret: <SECRET>
Content-Type: application/json
```

**Path Parameters** :
| Param | Type | Requis | Description |
|-------|------|--------|-------------|
| `user_id` | integer | ✅ | ID utilisateur DC360 |

**Réponse Attendue (200 OK)** :

```json
{
  "user_id": 42,
  "plan": "genesis_pro",
  "subscription_status": "active",
  "quota_limit": 50,
  "quota_used": 15,
  "quota_reset_date": "2025-12-01T00:00:00Z",
  "genesis_sessions_used": 15,
  "max_monthly_sessions": 50,
  "billing_cycle": "monthly",
  "subscription_start": "2025-11-01T00:00:00Z",
  "subscription_end": "2025-12-01T00:00:00Z"
}
```

**Champs JSON Requis (CRITIQUE)** :

| Champ | Type | Obligatoire | Description | Valeurs possibles |
|-------|------|-------------|-------------|-------------------|
| `plan` | string | ✅ | Plan d'abonnement | `trial`, `genesis_basic`, `genesis_pro`, `genesis_enterprise` |
| `subscription_status` | string | ✅ | Statut abonnement | `active`, `expired`, `cancelled`, `suspended` |
| `quota_limit` | integer | ✅ | Limite mensuelle briefs | Trial: 3, Basic: 10, Pro: 50, Enterprise: 999999 |
| `quota_used` | integer | ✅ | Briefs consommés ce mois | 0 à `quota_limit` |
| `quota_reset_date` | string (ISO 8601) | ✅ | Date reset quota | Format: `YYYY-MM-DDTHH:MM:SSZ` |

**Champs Optionnels** :
- `genesis_sessions_used` : Alias de `quota_used` (compatibilité)
- `max_monthly_sessions` : Alias de `quota_limit` (compatibilité)
- `billing_cycle` : Période facturation (`monthly`, `yearly`)
- `subscription_start` : Date début abonnement
- `subscription_end` : Date fin abonnement

**Réponses Erreur** :

```json
// 404 Not Found - Utilisateur inexistant
{
  "detail": "User not found",
  "error": "NOT_FOUND",
  "user_id": 999
}

// 403 Forbidden - Pas d'abonnement Genesis
{
  "detail": "User has no Genesis AI subscription",
  "error": "NO_SUBSCRIPTION",
  "user_id": 42
}
```

**Codes HTTP** :
- `200 OK` : Subscription récupérée
- `401 Unauthorized` : Authentification invalide
- `403 Forbidden` : Pas d'abonnement Genesis
- `404 Not Found` : Utilisateur inexistant
- `500 Internal Server Error` : Erreur serveur

---

### 3.2 Mock DC360 Subscription (Pour tests Genesis)

**Endpoint temporaire de test** :
```bash
# Mock à implémenter côté DC360 backend pour débloquer tests Genesis
GET /api/mock/users/{user_id}/subscription
```

**Réponse mock suggérée** :
```json
{
  "user_id": 42,
  "plan": "genesis_pro",
  "subscription_status": "active",
  "quota_limit": 50,
  "quota_used": 15,
  "quota_reset_date": "2025-12-01T00:00:00Z"
}
```

**⚠️ Note** : Ce mock permet à Genesis d'avancer ses tests sans attendre l'implémentation complète DC360.

---

## 4. CONFIGURATION ENVIRONNEMENT

### 4.1 Variables Genesis AI

```bash
# .env Genesis AI
ENVIRONMENT=development
DEBUG=true

# Service secret (identique à DC360)
GENESIS_SERVICE_SECRET=your-secret-here-min-32-chars

# DC360 API
DIGITALCLOUD360_API_URL=http://localhost:3000/api
DIGITALCLOUD360_SERVICE_SECRET=your-secret-here-min-32-chars

# Redis (persistance briefs)
REDIS_URL=redis://localhost:6379/0

# Providers LLM
DEEPSEEK_API_KEY=sk-...
KIMI_API_KEY=sk-...
OPENAI_API_KEY=sk-proj-...
```

### 4.2 Variables DC360

```bash
# .env DC360
# Service secret (identique à Genesis)
DIGITALCLOUD360_SERVICE_SECRET=your-secret-here-min-32-chars

# Genesis API
GENESIS_API_URL=http://localhost:8000/api/v1
GENESIS_SERVICE_SECRET=your-secret-here-min-32-chars

# Timeout
GENESIS_API_TIMEOUT=65  # > 60s pour génération briefs
```

---

## 5. TESTS D'INTÉGRATION

### 5.1 Test Genesis → DC360 (Vérification quotas)

**Commande cURL** :
```bash
curl -X GET \
  "http://localhost:3000/api/users/42/subscription" \
  -H "X-Service-Secret: your-secret-here" \
  -H "Content-Type: application/json"
```

**Résultat attendu** :
```json
{
  "plan": "genesis_pro",
  "quota_limit": 50,
  "quota_used": 15,
  ...
}
```

### 5.2 Test DC360 → Genesis (Récupération brief)

**Commande cURL** :
```bash
curl -X GET \
  "http://localhost:8000/api/v1/business-brief/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  -H "X-Service-Secret: your-secret-here" \
  -H "Content-Type: application/json"
```

**Résultat attendu** :
```json
{
  "brief_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "business_name": "TechHub Dakar",
  "results": { ... },
  ...
}
```

### 5.3 Checklist Validation Croisée

**Genesis valide** :
- [ ] Endpoint DC360 `/users/{id}/subscription` accessible
- [ ] Format JSON conforme (champs `plan`, `quota_limit`, `quota_used`, `quota_reset_date`)
- [ ] Header `X-Service-Secret` validé
- [ ] Codes erreur 404/403 cohérents

**DC360 valide** :
- [ ] Endpoint Genesis `/business-brief/{id}` accessible
- [ ] Payload JSON complet (research, content, logo, seo, template)
- [ ] Champs `results.content.homepage.fr` exploitables pour affichage
- [ ] Timeout > 60s configuré (génération peut prendre ~54s)

---

## 6. GESTION DES ERREURS

### 6.1 Quotas Dépassés

**Scénario** : User a consommé tous ses briefs du mois

**Comportement Genesis** :
```json
// 403 Forbidden
{
  "error": "QUOTA_EXCEEDED",
  "message": "Quota mensuel dépassé",
  "details": {
    "plan": "genesis_basic",
    "quota_limit": 10,
    "quota_used": 10,
    "quota_reset_date": "2025-12-01T00:00:00Z"
  }
}
```

**Action DC360 Frontend** : Afficher message upgrade plan

### 6.2 Timeout Génération

**Scénario** : Génération prend > 60s

**Comportement attendu** :
- Genesis : Continue génération (async)
- DC360 : Timeout côté client après 65s
- Solution : Implémenter polling ou webhooks (Phase 3)

### 6.3 Brief Expiré

**Scénario** : Brief demandé après TTL Redis (7 jours)

**Comportement Genesis** :
```json
// 404 Not Found
{
  "error": "BRIEF_EXPIRED",
  "message": "Ce brief a expiré et n'est plus disponible",
  "brief_id": "...",
  "ttl_days": 7
}
```

**Action DC360** : Message utilisateur "Brief expiré, régénérer ?"

---

## 7. LIMITATIONS & CONTRAINTES TECHNIQUES

### 7.1 Performance
- ⏱️ **Temps génération** : 50-60s moyenne (optimisable Phase 3)
- 🔄 **Rate limiting** : Recommandé 5 req/min par user
- 💾 **Taille payload** : ~50-100 KB par brief

### 7.2 Persistance
- ⏰ **TTL Redis** : 7 jours (604800s)
- 📦 **Backup PostgreSQL** : Optionnel (non implémenté Phase 2)

### 7.3 Langues
- ✅ **Supporté Phase 2** : Français uniquement
- 🔜 **Roadmap Phase 3** : Wolof, Anglais

### 7.4 Agents Legacy
- ❌ **Logo/SEO agents** : Non fonctionnels Phase 2
- ✅ **Template selection** : Opérationnel
- 🔜 **Fix prévu** : Sprint 4

---

## 8. SÉQUENCE DIAGRAM WORKFLOW COMPLET

```
┌────────┐         ┌─────────┐          ┌─────────┐          ┌─────────┐
│  User  │         │ DC360   │          │ DC360   │          │ Genesis │
│ (Web)  │         │Frontend │          │Backend  │          │   AI    │
└───┬────┘         └────┬────┘          └────┬────┘          └────┬────┘
    │                   │                    │                    │
    │ 1. Wizard Start   │                    │                    │
    │──────────────────▶│                    │                    │
    │                   │                    │                    │
    │                   │ 2. Check Quota     │                    │
    │                   │───────────────────▶│                    │
    │                   │                    │                    │
    │                   │                    │ 3. GET /users/42/subscription
    │                   │                    │───────────────────▶│
    │                   │                    │                    │
    │                   │                    │ 4. Subscription    │
    │                   │                    │◀───────────────────│
    │                   │                    │   {quota: 35/50}   │
    │                   │                    │                    │
    │                   │ 5. Quota OK ✅     │                    │
    │                   │◀───────────────────│                    │
    │                   │                    │                    │
    │ 6. Fill Form      │                    │                    │
    │──────────────────▶│                    │                    │
    │                   │                    │                    │
    │ 7. Submit         │                    │                    │
    │──────────────────▶│                    │                    │
    │                   │                    │                    │
    │                   │ 8. POST /business-brief/generate        │
    │                   │───────────────────▶│───────────────────▶│
    │                   │                    │   X-Service-Secret │
    │                   │                    │                    │
    │ 9. Loading...     │                    │  10. Orchestration │
    │◀──────────────────│                    │     (~54s)         │
    │   (Progress UI)   │                    │     [Kimi, Deepseek│
    │                   │                    │      Redis]        │
    │                   │                    │                    │
    │                   │                    │ 11. Brief Ready    │
    │                   │                    │◀───────────────────│
    │                   │                    │   {brief_id: ...}  │
    │                   │                    │                    │
    │                   │ 12. Brief ID       │                    │
    │                   │◀───────────────────│                    │
    │                   │                    │                    │
    │                   │ 13. GET /business-brief/{id}            │
    │                   │───────────────────▶│───────────────────▶│
    │                   │                    │                    │
    │                   │                    │ 14. Full Brief     │
    │                   │                    │◀───────────────────│
    │                   │                    │   {results: {...}} │
    │                   │                    │                    │
    │                   │ 15. Display Brief  │                    │
    │                   │◀───────────────────│                    │
    │                   │                    │                    │
    │ 16. Preview ✅    │                    │                    │
    │◀──────────────────│                    │                    │
    │                   │                    │                    │
    │ 17. Create Site   │                    │                    │
    │──────────────────▶│                    │                    │
    │                   │                    │                    │
    │                   │ 18. DC360 Website Creation              │
    │                   │───────────────────▶│                    │
    │                   │   (using brief     │                    │
    │                   │    content)        │                    │
    │                   │                    │                    │
```

---

## 9. PROCHAINES ÉTAPES (POST-PHASE 2)

### Phase 3 : Optimisations
- ⚡ Parallélisation appels API Deepseek (cible < 40s)
- 🔔 Webhooks notifications brief ready
- 📊 Endpoint GET `/business-brief/{id}/status` (progression)

### Phase 4 : Features Avancées
- 🌐 Support multilingue (Wolof, Anglais)
- 🎨 Fix agents Logo/SEO
- 💾 Backup PostgreSQL automatique
- 📈 Analytics & monitoring

---

## 10. CONTACTS & SUPPORT

**Tech Lead Genesis AI** : agnissaneric (agnissan@digital.ci)
**Tech Lead DC360** : TBD
**Scrum Master** : Cascade

**Channels communication** :
- 💬 Slack : `#genesis-dc360-integration`
- 📧 Email : équipes techniques
- 🐛 Issues : GitHub repository

---

## 11. VALIDATION & SIGNATURE

### Checklist Pré-déploiement Phase 2

**Genesis AI** :
- [x] Documentation Swagger à jour
- [x] Endpoint GET `/business-brief/{id}` opérationnel
- [x] Endpoint GET `/business-brief/user/{id}` opérationnel
- [x] Auth `X-Service-Secret` implémentée
- [ ] Tests intégration avec mock DC360 (en attente mock)
- [x] JSON Schema validé

**DC360** :
- [ ] Endpoint GET `/users/{id}/subscription` implémenté (mock suffisant Phase 2)
- [ ] Frontend Wizard appels Genesis configurés
- [ ] Timeout client > 60s
- [ ] Gestion erreurs 403 Quota
- [ ] Tests avec vrais payloads Genesis

---

**VERSION** : 1.0.0
**DATE CRÉATION** : 2025-11-22
**DERNIÈRE MAJ** : 2025-11-22
**STATUT** : 🟢 VALIDÉ - Prêt pour implémentation Phase 2

---

**Signature Tech Lead Genesis AI**
*agnissaneric - 2025-11-22*
