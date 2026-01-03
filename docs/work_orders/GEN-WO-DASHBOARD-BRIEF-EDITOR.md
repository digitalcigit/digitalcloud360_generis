---
title: "Work Order: Dashboard Sites + Business Brief Editor"
code: "GEN-WO-DASHBOARD-BRIEF"
date: "2026-01-03"
status: "draft"
priority: "haute"
estimation: "2-3 sprints"
tags: ["dashboard", "brief-editor", "frontend", "backend", "ux"]
---

# GEN-WO-DASHBOARD-BRIEF: Dashboard Sites + Business Brief Editor

## 1. Contexte et Objectif

### 1.1 Besoin Utilisateur
L'utilisateur génère un site via le coaching Genesis et souhaite :
1. **Retrouver** son site à tout moment (lien permanent)
2. **Consulter** le résumé du coaching (Business Brief)
3. **Modifier** ce résumé pour l'améliorer
4. **Régénérer** le site avec les modifications

### 1.2 Objectif Technique
Créer un Dashboard permettant de :
- Lister tous les sites générés par l'utilisateur
- Afficher et éditer le Business Brief associé à chaque site
- Synchroniser les modifications du Brief vers le Site (re-transformation)

---

## 2. Analyse de l'Existant

### 2.1 Structure Frontend Actuelle

```
genesis-frontend/src/
├── app/
│   ├── (auth)/auth/callback/     # Callback SSO
│   ├── api/                      # API Routes Next.js
│   │   ├── auth/                 # Auth endpoints
│   │   └── coaching/             # Coaching endpoints
│   ├── coaching/                 # Pages coaching
│   │   └── onboarding/           # Étape 0
│   ├── genesis/themes/           # Sélection thème
│   ├── login/                    # Page login
│   ├── preview/[siteId]/         # ✅ EXISTE - Preview site
│   └── sites/[id]/               # ⚠️ EXISTE MAIS INCOMPLET
├── components/
│   ├── blocks/                   # Blocs du site (Hero, About, etc.)
│   ├── coaching/                 # Composants coaching
│   ├── BlockRenderer.tsx         # Rendu dynamique blocs
│   ├── SiteRenderer.tsx          # Rendu site complet
│   └── PreviewToolbar.tsx        # Toolbar preview
├── stores/
│   └── useAuthStore.ts           # Store auth (Zustand)
├── types/
│   └── site-definition.ts        # Types SiteDefinition
└── utils/
    └── api.ts                    # Fonctions API
```

#### Routes Existantes Pertinentes

| Route | Fichier | État | Description |
|-------|---------|------|-------------|
| `/preview/[siteId]` | `preview/[siteId]/page.tsx` | ✅ Complet | Preview site avec toolbar viewport |
| `/sites/[id]` | `sites/[id]/page.tsx` | ⚠️ Partiel | Affiche site mais sans dashboard |

#### Composants Réutilisables

| Composant | Fichier | Utilité pour Dashboard |
|-----------|---------|------------------------|
| `SiteRenderer` | `SiteRenderer.tsx` | Embed preview dans dashboard |
| `PreviewToolbar` | `PreviewToolbar.tsx` | Toolbar viewport (mobile/tablet/desktop) |
| `BlockRenderer` | `BlockRenderer.tsx` | Rendu blocs individuels |

### 2.2 APIs Backend Existantes

```
app/api/v1/
├── auth.py          # Authentification
├── coaching.py      # ✅ Sessions coaching + Brief
├── genesis.py       # ✅ CRUD Business Brief (Redis)
├── sites.py         # ✅ Génération + Récupération sites
├── themes.py        # ✅ Sélection thème + Génération
└── users.py         # Gestion utilisateurs
```

#### Endpoints Existants Pertinents

| Méthode | Endpoint | Fichier | Description |
|---------|----------|---------|-------------|
| `GET` | `/coaching/{session_id}/site` | coaching.py:541 | Récupère SiteDefinition depuis Redis |
| `GET` | `/genesis/business-brief/{brief_id}` | genesis.py:259 | Récupère BusinessBrief depuis Redis |
| `DELETE` | `/genesis/business-brief/{brief_id}` | genesis.py:316 | Supprime BusinessBrief |
| `POST` | `/sites/generate` | sites.py:112 | Génère site depuis brief_id |
| `GET` | `/sites/{site_id}` | sites.py:192 | Récupère site existant |
| `GET` | `/sites/{site_id}/preview` | sites.py:217 | Récupère SiteDefinition seul |

#### ⚠️ Endpoints MANQUANTS à Créer

| Méthode | Endpoint | Description | Priorité |
|---------|----------|-------------|----------|
| `GET` | `/users/me/sites` | **Liste tous les sites de l'utilisateur** | P0 |
| `PATCH` | `/briefs/{brief_id}` | **Modifier un BusinessBrief** | P0 |
| `POST` | `/briefs/{brief_id}/apply` | **Régénérer site depuis brief modifié** | P1 |
| `GET` | `/coaching/{session_id}/conversation` | Récupérer historique conversation | P2 |

### 2.3 Modèles de Données

#### Base de Données PostgreSQL

```python
# app/models/coaching.py

class BusinessBrief(BaseModel):
    __tablename__ = "business_briefs"
    
    coaching_session_id = Column(Integer, ForeignKey("coaching_sessions.id"))
    business_name = Column(String, nullable=False)
    vision = Column(Text, nullable=False)
    mission = Column(Text, nullable=False)
    target_audience = Column(Text, nullable=False)
    differentiation = Column(Text, nullable=False)
    value_proposition = Column(Text, nullable=False)
    sector = Column(String, nullable=False)
    location = Column(JSON)
    
    # Sub-agents results
    market_research = Column(JSON)
    content_generation = Column(JSON)
    logo_creation = Column(JSON)
    seo_optimization = Column(JSON)
    template_selection = Column(JSON)

class CoachingSession(BaseModel):
    __tablename__ = "coaching_sessions"
    
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String, unique=True)  # UUID
    status = Column(Enum(SessionStatusEnum))
    current_step = Column(Enum(CoachingStepEnum))
    conversation_history = Column(JSON)       # ✅ Historique chat
```

```python
# app/models/site.py

class Site(BaseModel):
    __tablename__ = "sites"
    
    user_id = Column(Integer, ForeignKey("users.id"))
    brief_id = Column(Integer, ForeignKey("business_briefs.id"))
    definition = Column(JSON)  # SiteDefinition complet
    status = Column(Enum(SiteStatusEnum))
```

#### Redis (Cache)

```
# Clés Redis actuelles
session:{session_uuid}     → Session data + onboarding
onboarding:{session_uuid}  → Données onboarding (redondant)
site:{session_uuid}        → SiteDefinition JSON (TTL 24h)

# Exemple de site en Redis
site:c70b2dfc-1547-4aca-93e4-89ef5cc2f20a → {
  "metadata": { "name": "...", "theme": "savor" },
  "theme": { "colors": {...}, "fonts": {...} },
  "pages": [{ "slug": "/", "sections": [...] }]
}
```

### 2.4 Flux de Données Actuel

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Onboarding    │────▶│    Coaching     │────▶│  Theme Select   │
│  (Étape 0)      │     │  (Étapes 1-5)   │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Redis: session  │     │ DB: BusinessBrief│    │ Redis: site     │
│ + onboarding    │     │ + CoachingSteps │     │ (SiteDefinition)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │ /preview/{uuid} │
                                                │  (Frontend)     │
                                                └─────────────────┘
```

---

## 3. Architecture Cible

### 3.1 Nouvelles Routes Frontend

```
genesis-frontend/src/app/
├── dashboard/                           # NOUVEAU
│   ├── page.tsx                         # Redirect vers /sites
│   ├── layout.tsx                       # Layout dashboard
│   └── sites/                           
│       ├── page.tsx                     # Liste des sites
│       └── [siteId]/
│           ├── page.tsx                 # Vue détail site
│           ├── brief/
│           │   └── page.tsx             # Éditeur Business Brief
│           └── settings/
│               └── page.tsx             # Paramètres site (futur)
```

### 3.2 Nouveaux Composants

```
genesis-frontend/src/components/
├── dashboard/                           # NOUVEAU
│   ├── DashboardLayout.tsx              # Layout avec sidebar
│   ├── SiteCard.tsx                     # Card site dans liste
│   ├── SitesList.tsx                    # Liste des sites
│   ├── SiteDetailHeader.tsx             # Header page détail
│   └── SitePreviewEmbed.tsx             # Embed preview
├── brief/                               # NOUVEAU
│   ├── BusinessBriefPanel.tsx           # Panel affichage brief
│   ├── BriefFieldEditor.tsx             # Éditeur inline champ
│   ├── BriefSyncDialog.tsx              # Dialog "Appliquer au site"
│   └── ConversationHistoryModal.tsx     # Modal historique chat
```

### 3.3 Nouveaux Endpoints Backend

```python
# app/api/v1/dashboard.py (NOUVEAU)

@router.get("/sites")
async def list_user_sites(current_user: User) -> List[SiteListItem]:
    """Liste tous les sites de l'utilisateur avec métadonnées"""
    pass

@router.get("/sites/{session_id}/brief")
async def get_site_brief(session_id: str, current_user: User) -> BusinessBriefResponse:
    """Récupère le BusinessBrief associé à un site"""
    pass

@router.patch("/sites/{session_id}/brief")
async def update_site_brief(session_id: str, updates: BriefUpdateRequest, current_user: User):
    """Met à jour les champs du BusinessBrief"""
    pass

@router.post("/sites/{session_id}/regenerate")
async def regenerate_site(session_id: str, current_user: User):
    """Régénère le site avec le Brief actuel"""
    pass

@router.get("/sites/{session_id}/conversation")
async def get_conversation_history(session_id: str, current_user: User) -> ConversationResponse:
    """Récupère l'historique de conversation coaching"""
    pass
```

### 3.4 Schémas API

```python
# app/schemas/dashboard.py (NOUVEAU)

class SiteListItem(BaseModel):
    session_id: str
    business_name: str
    sector: str
    theme_name: str
    theme_slug: str
    preview_url: str
    created_at: datetime
    updated_at: datetime
    status: str

class BusinessBriefResponse(BaseModel):
    session_id: str
    business_name: str
    vision: str
    mission: str
    target_audience: str
    differentiation: str
    value_proposition: str
    sector: str
    logo_url: Optional[str]
    created_at: datetime
    updated_at: datetime

class BriefUpdateRequest(BaseModel):
    business_name: Optional[str]
    vision: Optional[str]
    mission: Optional[str]
    target_audience: Optional[str]
    differentiation: Optional[str]
    value_proposition: Optional[str]

class ConversationMessage(BaseModel):
    role: str  # "coach" | "user"
    content: str
    step: str
    timestamp: datetime

class ConversationResponse(BaseModel):
    session_id: str
    messages: List[ConversationMessage]
```

---

## 4. Plan d'Implémentation

### Sprint 1: Dashboard Liste Sites (3-4 jours)

#### Backend (1.5 jours)
- [ ] Créer `app/api/v1/dashboard.py`
- [ ] Implémenter `GET /dashboard/sites` (liste sites utilisateur)
- [ ] Créer `app/schemas/dashboard.py` avec `SiteListItem`
- [ ] Requête SQL: joindre `coaching_sessions` + `business_briefs` + Redis sites
- [ ] Tests unitaires endpoint

#### Frontend (1.5 jours)
- [ ] Créer structure routes `/dashboard/sites`
- [ ] Créer `DashboardLayout.tsx` avec sidebar minimale
- [ ] Créer `SiteCard.tsx` (preview thumbnail, nom, date, boutons)
- [ ] Créer `SitesList.tsx` avec grid responsive
- [ ] Intégrer appel API `getUserSites()`
- [ ] État vide "Aucun site" avec CTA vers coaching

#### Livrables Sprint 1
```
✅ Route /dashboard/sites accessible
✅ Liste des sites générés avec preview
✅ Lien vers /preview/{sessionId}
✅ Responsive (mobile/desktop)
```

### Sprint 2: Vue Détail + Brief Lecture (3-4 jours)

#### Backend (1 jour)
- [ ] Implémenter `GET /dashboard/sites/{session_id}/brief`
- [ ] Récupérer BusinessBrief depuis DB + enrichir avec onboarding Redis
- [ ] Implémenter `GET /dashboard/sites/{session_id}/conversation`
- [ ] Parser `conversation_history` JSON depuis CoachingSession

#### Frontend (2-3 jours)
- [ ] Créer `/dashboard/sites/[siteId]/page.tsx`
- [ ] Créer `SiteDetailHeader.tsx` (nom, statut, actions)
- [ ] Créer `SitePreviewEmbed.tsx` (iframe ou composant)
- [ ] Créer `BusinessBriefPanel.tsx` (affichage lecture seule)
- [ ] Créer `ConversationHistoryModal.tsx`
- [ ] Intégrer appels API

#### Livrables Sprint 2
```
✅ Route /dashboard/sites/{id} accessible
✅ Preview du site embarqué
✅ Affichage Business Brief complet
✅ Modal "Voir la conversation"
```

### Sprint 3: Brief Editor + Sync (4-5 jours)

#### Backend (2 jours)
- [ ] Implémenter `PATCH /dashboard/sites/{session_id}/brief`
- [ ] Validation des champs modifiables
- [ ] Mise à jour DB `business_briefs`
- [ ] Implémenter `POST /dashboard/sites/{session_id}/regenerate`
- [ ] Réutiliser `BriefToSiteTransformer.transform()`
- [ ] Mettre à jour Redis `site:{session_id}`
- [ ] Versionning basique (stocker ancienne version)

#### Frontend (2-3 jours)
- [ ] Créer `/dashboard/sites/[siteId]/brief/page.tsx`
- [ ] Créer `BriefFieldEditor.tsx` (édition inline avec save)
- [ ] Créer `BriefSyncDialog.tsx` (preview diff + confirmation)
- [ ] Gestion état "modifié non sauvegardé"
- [ ] Toast notifications (succès/erreur)
- [ ] Bouton "Régénérer le site"

#### Livrables Sprint 3
```
✅ Édition inline de chaque champ du Brief
✅ Sauvegarde automatique ou manuelle
✅ Dialog confirmation avant régénération
✅ Régénération site avec nouveau brief
```

---

## 5. Maquettes UX

### 5.1 Dashboard Sites List

```
┌─────────────────────────────────────────────────────────────────────┐
│  🏠 Genesis                                    [User Menu ▼]        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Mes Sites                                    [+ Créer un site]     │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │     │
│  │ │  Preview    │ │  │ │  Preview    │ │  │ │  Preview    │ │     │
│  │ │  Thumbnail  │ │  │ │  Thumbnail  │ │  │ │  Thumbnail  │ │     │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │     │
│  │                 │  │                 │  │                 │     │
│  │ Savor V2 Fix    │  │ Mon Salon       │  │ TechStartup     │     │
│  │ 🍽️ Restaurant   │  │ 💇 Beauté       │  │ 💻 Tech         │     │
│  │                 │  │                 │  │                 │     │
│  │ 3 jan 2026      │  │ 28 déc 2025     │  │ 15 déc 2025     │     │
│  │                 │  │                 │  │                 │     │
│  │ [Voir] [Éditer] │  │ [Voir] [Éditer] │  │ [Voir] [Éditer] │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Site Detail + Brief Panel

```
┌─────────────────────────────────────────────────────────────────────┐
│  ← Retour aux sites     Savor V2 Fix            [🔗 Lien] [⚙️]     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────┐  ┌─────────────────────┐  │
│  │                                     │  │ 📋 BUSINESS BRIEF   │  │
│  │                                     │  │                     │  │
│  │                                     │  │ 👁️ Vision           │  │
│  │          SITE PREVIEW               │  │ ┌─────────────────┐ │  │
│  │          (iframe/embed)             │  │ │ Créer un lieu   │ │  │
│  │                                     │  │ │ de vie où...    │ │  │
│  │                                     │  │ └─────────────────┘ │  │
│  │                                     │  │                     │  │
│  │                                     │  │ 🎯 Mission          │  │
│  │                                     │  │ ┌─────────────────┐ │  │
│  │  [📱] [📟] [🖥️]                     │  │ │ Proposer une    │ │  │
│  │                                     │  │ │ cuisine...      │ │  │
│  └─────────────────────────────────────┘  │ └─────────────────┘ │  │
│                                           │                     │  │
│                                           │ [✏️ Modifier Brief] │  │
│                                           │ [💬 Voir convo]     │  │
│                                           └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.3 Brief Editor (Inline)

```
┌─────────────────────────────────────────────────────────────────────┐
│  ← Retour     Modifier le Business Brief        [Annuler] [💾 Save] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  👁️ VISION                                              [✨ IA]    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Créer un lieu de vie où la cuisine devient une expérience   │   │
│  │ de partage et de découverte pour les familles dakaroises.   │   │
│  │                                                         ✏️  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  🎯 MISSION                                             [✨ IA]    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Proposer une cuisine authentique avec des produits frais    │   │
│  │ locaux, dans une ambiance chaleureuse et familiale.         │   │
│  │                                                         ✏️  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  👥 CLIENTÈLE CIBLE                                     [✨ IA]    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Familles avec enfants, couples, groupes d'amis cherchant    │   │
│  │ une sortie gourmande le week-end.                           │   │
│  │                                                         ✏️  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ⭐ DIFFÉRENCIATION                                     [✨ IA]    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Fusion cuisine sénégalaise et française, chef formé à       │   │
│  │ Paris, terrasse avec vue sur la corniche.                   │   │
│  │                                                         ✏️  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  💼 PROPOSITION DE VALEUR                               [✨ IA]    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Menu dégustation à prix accessible avec accord mets-vins    │   │
│  │ locaux. Espace enfants sécurisé.                            │   │
│  │                                                         ✏️  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ⚠️ Modifications non appliquées au site                           │
│  [🔄 Régénérer le site avec ces modifications]                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Points d'Attention

### 6.1 Sécurité
- **Ownership**: Toujours vérifier que le site/brief appartient à `current_user`
- **Validation**: Valider tous les inputs avant modification DB
- **Rate limiting**: Limiter les régénérations (coût IA)

### 6.2 Performance
- **Pagination**: Prévoir pagination si > 10 sites
- **Cache**: Utiliser Redis pour les données fréquentes
- **Lazy loading**: Charger thumbnails à la demande

### 6.3 UX
- **Feedback**: Toast notifications pour toutes actions
- **Autosave**: Considérer autosave avec debounce
- **Confirmation**: Dialog avant régénération (action coûteuse)

### 6.4 Compatibilité
- **Mobile first**: Dashboard utilisable sur mobile
- **Accessibilité**: Labels ARIA, navigation clavier

---

## 7. Dépendances

### Frontend
```json
{
  "dependencies": {
    "zustand": "^4.x",           // ✅ Déjà installé (store)
    "@tanstack/react-query": "",  // À ajouter (cache API)
    "sonner": ""                  // À ajouter (toasts)
  }
}
```

### Backend
- Pas de nouvelles dépendances requises

---

## 8. Tests

### Tests Backend
```python
# tests/api/test_dashboard.py

async def test_list_user_sites_empty():
    """Utilisateur sans sites retourne liste vide"""
    
async def test_list_user_sites_with_data():
    """Utilisateur avec sites retourne liste correcte"""
    
async def test_get_brief_not_found():
    """Brief inexistant retourne 404"""
    
async def test_get_brief_unauthorized():
    """Brief d'un autre user retourne 403"""
    
async def test_update_brief_success():
    """Modification brief réussie"""
    
async def test_regenerate_site_success():
    """Régénération site après modif brief"""
```

### Tests Frontend (Playwright)
```typescript
// e2e/dashboard.spec.ts

test('user can view sites list', async ({ page }) => {});
test('user can open site detail', async ({ page }) => {});
test('user can view business brief', async ({ page }) => {});
test('user can edit brief field inline', async ({ page }) => {});
test('user can regenerate site', async ({ page }) => {});
```

---

## 9. Critères d'Acceptation

### Sprint 1
- [ ] `/dashboard/sites` affiche la liste des sites de l'utilisateur
- [ ] Chaque site affiche : nom, secteur, date, preview thumbnail
- [ ] Clic sur "Voir" ouvre `/preview/{sessionId}`
- [ ] Responsive mobile/desktop

### Sprint 2
- [ ] `/dashboard/sites/{id}` affiche le détail du site
- [ ] Preview du site embarqué avec contrôle viewport
- [ ] Business Brief affiché en lecture
- [ ] Historique conversation accessible

### Sprint 3
- [ ] Édition inline de chaque champ du Brief
- [ ] Sauvegarde des modifications
- [ ] Régénération du site avec confirmation
- [ ] Feedback utilisateur (toasts)

---

## 10. Fichiers à Créer/Modifier

### Backend (Nouveaux)
```
app/api/v1/dashboard.py          # Endpoints dashboard
app/schemas/dashboard.py         # Schémas Pydantic
tests/api/test_dashboard.py      # Tests unitaires
```

### Backend (Modifier)
```
app/api/v1/__init__.py           # Ajouter router dashboard
```

### Frontend (Nouveaux)
```
src/app/dashboard/layout.tsx
src/app/dashboard/page.tsx
src/app/dashboard/sites/page.tsx
src/app/dashboard/sites/[siteId]/page.tsx
src/app/dashboard/sites/[siteId]/brief/page.tsx
src/components/dashboard/DashboardLayout.tsx
src/components/dashboard/SiteCard.tsx
src/components/dashboard/SitesList.tsx
src/components/dashboard/SiteDetailHeader.tsx
src/components/dashboard/SitePreviewEmbed.tsx
src/components/brief/BusinessBriefPanel.tsx
src/components/brief/BriefFieldEditor.tsx
src/components/brief/BriefSyncDialog.tsx
src/components/brief/ConversationHistoryModal.tsx
src/utils/dashboard-api.ts
```

### Frontend (Modifier)
```
src/utils/api.ts                 # Ajouter fonctions dashboard
```

---

*Work Order créé le 03/01/2026 - En attente validation PM*
