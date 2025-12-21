# GEN-WO-005: Sprint 3 - Intégration Site Renderer

---
title: "Sprint 3 - Intégration Site Renderer Next.js"
tags: ["frontend", "next.js", "site-renderer", "integration", "sprint3"]
status: "ready"
date: "2025-12-21"
priority: "HIGH"
assignee: "Senior Dev"
branch: "feature/gen-wo-005-site-renderer-integration"
---

## 📋 Contexte

Le **Sprint 3 Backend** est maintenant **VALIDÉ** ✅ :
- Tous les agents (Logo DALL-E, SEO Deepseek) fonctionnent
- Le `site_data` est correctement généré avec 5 sections (hero, about, features, contact, footer)
- L'orchestration LangGraph retourne `successful_agents=5/5`

**Constat après analyse du frontend existant** : Le Site Renderer est **DÉJÀ implémenté** à 90% !
- `BlockRenderer.tsx` ✅ (dynamic imports pour 10 types de blocks)
- `SiteRenderer.tsx` ✅ (ThemeProvider + PageRenderer)
- `PageRenderer.tsx` ✅ (itère sur sections)
- Routes `/preview/[siteId]` et `/sites/[id]` ✅

**Problème identifié** : L'intégration finale entre le coaching et le preview est cassée.

## 🎯 Objectif

Permettre à l'utilisateur de visualiser son site généré après le coaching :
```
Coaching Terminé → Bouton "Voir mon site" → /preview/{sessionId} → Site affiché
```

## 🔴 Problème Principal

Dans `CoachingInterface.tsx` ligne 250 :
```typescript
// ❌ ACTUEL - redirige vers /preview sans ID
onClick={() => router.push('/preview')}

// ✅ ATTENDU - redirige avec le sessionId
onClick={() => router.push(`/preview/${sessionId}`)}
```

## 📐 Architecture Existante

### Frontend (Next.js 14)
```
genesis-frontend/src/
├── app/
│   ├── preview/[siteId]/page.tsx    # ✅ Existe - utilise getSitePreview()
│   └── sites/[id]/page.tsx          # ✅ Existe - utilise getSite()
├── components/
│   ├── BlockRenderer.tsx            # ✅ Complet - 10 types de blocks
│   ├── SiteRenderer.tsx             # ✅ Complet - ThemeProvider + PageRenderer
│   ├── PageRenderer.tsx             # ✅ Complet - Itère sur sections
│   ├── blocks/                      # ✅ Complet - 10 composants
│   │   ├── HeroBlock.tsx
│   │   ├── AboutBlock.tsx
│   │   ├── FeaturesBlock.tsx
│   │   ├── ContactBlock.tsx
│   │   ├── FooterBlock.tsx
│   │   └── ... (5 autres)
│   └── coaching/
│       └── CoachingInterface.tsx    # ⚠️ À modifier - redirection cassée
├── types/
│   ├── site-definition.ts           # ✅ Types complets
│   └── blocks/                      # ✅ Types pour chaque block
└── utils/
    └── api.ts                       # ✅ getSitePreview(), getSite()
```

### Backend (FastAPI)
```
app/api/v1/
├── coaching.py      # ✅ Retourne site_data + sauvegarde Redis avec session_id
└── sites.py         # ✅ GET /{site_id}/preview - Retourne site_definition
```

### Flux de Données
```
1. Coaching terminé (étape OFFRE complète)
   └── coaching.py ligne 263-267 :
       await redis_client.set(f"site:{session_id}", json.dumps(site_definition))
       return CoachingResponse(site_data=site_definition)

2. Frontend reçoit site_data
   └── CoachingInterface.tsx vérifie coachingState.site_data

3. Redirection (À CORRIGER)
   └── Doit utiliser sessionId pour construire /preview/{sessionId}

4. Preview Page charge le site
   └── /preview/[siteId]/page.tsx appelle getSitePreview(siteId)
   └── Backend GET /sites/{siteId}/preview retourne le site_definition
```

## ✅ Tâches à Réaliser

### Tâche 1: Corriger la redirection CoachingInterface (5 min)

**Fichier**: `genesis-frontend/src/components/coaching/CoachingInterface.tsx`

**Modification ligne 250** :
```typescript
// AVANT
onClick={() => router.push('/preview')}

// APRÈS
onClick={() => router.push(`/preview/${sessionId}`)}
```

### Tâche 2: Adapter l'endpoint backend pour Redis key (10 min)

**Fichier**: `app/api/v1/sites.py`

Le coaching sauvegarde avec la clé `site:{session_id}` mais l'endpoint `/sites/{site_id}/preview` 
utilise `redis_fs.read_session()` qui cherche avec un préfixe différent.

**Option A** : Modifier le coaching pour utiliser le même format que sites.py
**Option B** : Ajouter un endpoint dédié `/coaching/{session_id}/site`

**Recommandation** : Option B - Plus propre, séparation des responsabilités.

```python
# Nouveau endpoint dans coaching.py
@router.get("/{session_id}/site", response_model=Dict[str, Any])
async def get_coaching_site(
    session_id: str,
    current_user = Depends(get_current_user),
    redis_client = Depends(get_redis_client)
) -> Dict[str, Any]:
    """Retourne le SiteDefinition généré pour une session coaching."""
    site_data = await redis_client.get(f"site:{session_id}")
    if not site_data:
        raise HTTPException(status_code=404, detail="Site not found for this session")
    return json.loads(site_data)
```

### Tâche 3: Adapter le frontend pour le nouvel endpoint (10 min)

**Fichier**: `genesis-frontend/src/utils/api.ts`

Ajouter une fonction pour récupérer le site depuis le session_id :
```typescript
export async function getCoachingSite(sessionId: string, token: string): Promise<SiteDefinition> {
    const response = await fetch(`${API_BASE_URL}/coaching/${sessionId}/site`, {
        headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!response.ok) throw new Error('Failed to fetch coaching site');
    return response.json();
}
```

**Fichier**: `genesis-frontend/src/app/preview/[siteId]/page.tsx`

Modifier pour utiliser le nouvel endpoint si le siteId ressemble à un UUID de session :
```typescript
// Dans fetchPreview()
const siteDefinition = siteId.includes('-') 
    ? await getCoachingSite(siteId, token)  // Session ID (UUID)
    : await getSitePreview(siteId, token);   // Site ID legacy
```

### Tâche 4: Test E2E manuel (10 min)

1. Démarrer l'environnement Docker :
   ```bash
   docker-compose up -d genesis-api frontend
   ```

2. Ouvrir le navigateur : `http://localhost:3002/coaching`

3. Compléter les 5 étapes du coaching avec des réponses riches

4. Cliquer sur "Voir mon site" → Vérifier l'affichage du site

5. Vérifier les sections affichées :
   - Hero avec titre et CTA
   - About avec description
   - Features/Services
   - Contact
   - Footer avec logo

## 🐳 Environnement Docker

**IMPORTANT** : Tout développement et test doit se faire dans l'environnement containerisé.

### Commandes utiles

```bash
# Démarrer les services
docker-compose up -d genesis-api frontend redis postgres

# Logs en temps réel
docker-compose logs -f genesis-api frontend

# Rebuild après modifications frontend
docker-compose up -d --build frontend

# Rebuild après modifications backend
docker-compose restart genesis-api

# Test manuel backend (dans container)
docker exec genesis-api python tests/manual_test_sprint3.py
```

### Ports
| Service | Port Hôte | URL |
|---------|-----------|-----|
| Frontend Next.js | 3002 | http://localhost:3002 |
| API FastAPI | 8002 | http://localhost:8002 |
| Redis | 6379 | localhost:6379 |

## 📝 Git Workflow

### Branche dédiée obligatoire
```bash
git checkout master
git pull origin master
git checkout -b feature/gen-wo-005-site-renderer-integration
```

### Commits atomiques
```bash
git add genesis-frontend/src/components/coaching/CoachingInterface.tsx
git commit -m "fix(coaching): redirect to preview with sessionId"

git add app/api/v1/coaching.py
git commit -m "feat(coaching): add GET /{session_id}/site endpoint"

git add genesis-frontend/src/utils/api.ts genesis-frontend/src/app/preview/[siteId]/page.tsx
git commit -m "feat(frontend): integrate coaching site endpoint"
```

### Pull Request
```bash
git push origin feature/gen-wo-005-site-renderer-integration
# Créer PR vers master avec description des changements
```

## ✅ Critères d'Acceptation

- [ ] Après coaching terminé, bouton "Voir mon site" redirige vers `/preview/{sessionId}`
- [ ] Le site s'affiche avec les 5 sections (hero, about, features, contact, footer)
- [ ] Le logo DALL-E s'affiche (pas de placeholder)
- [ ] Les couleurs du thème sont appliquées
- [ ] Le titre SEO apparaît dans la page
- [ ] Test E2E complet réussi du coaching jusqu'à l'affichage du site

## 📊 Estimation

| Tâche | Temps estimé |
|-------|--------------|
| Correction redirection | 5 min |
| Nouvel endpoint backend | 10 min |
| Adaptation frontend | 10 min |
| Tests E2E | 10 min |
| **Total** | **~35 min** |

## 📚 Fichiers de Référence

- Backend transformer : `app/services/transformer.py`
- Types SiteDefinition : `genesis-frontend/src/types/site-definition.ts`
- Block components : `genesis-frontend/src/components/blocks/`
- Test E2E backend : `tests/manual_test_sprint3.py`

## 🔗 Dépendances

- **Prérequis** : Sprint 3 Backend validé ✅ (commit `a344fc81`)
- **Bloqué par** : Rien
- **Bloque** : Phase 2 - Édition conversationnelle du site

---

**Rédigé par** : Tech Lead (Cascade)  
**Date** : 2025-12-21  
**Statut** : Prêt pour développement
