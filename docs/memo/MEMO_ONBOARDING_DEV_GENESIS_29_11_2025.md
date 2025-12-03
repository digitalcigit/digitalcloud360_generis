---
title: "Onboarding Développeur - Genesis AI Frontend"
from: "Tech Lead Genesis AI"
to: "Nouveau Développeur Frontend"
date: "29 novembre 2025"
priority: "HIGH"
status: "MISSION_ACTIVE"
tags: ["onboarding", "frontend", "sso", "security", "docker"]
---

# 🚀 MÉMO D'ONBOARDING - Genesis AI Frontend

Bienvenue dans l'équipe Genesis AI ! Ce mémo te donne le contexte, le périmètre de travail, et les règles à respecter pour contribuer efficacement au projet.

---

## 1. Contexte Projet

### 1.1 Vision Genesis AI

Genesis AI est un **Partenaire Digital Intelligent** pour entrepreneurs africains. Il permet de :
- Générer un **Business Brief** via conversation IA (chat)
- Transformer ce brief en **site web** automatiquement
- Offrir un accompagnement continu (coaching digital)

### 1.2 Architecture Écosystème

```
┌─────────────────────────────────────────────────────────────────┐
│                    ÉCOSYSTÈME DC360                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────┐         ┌─────────────────────────────┐  │
│   │   DC360 Hub     │         │      Genesis AI             │  │
│   │   (Satellite)   │         │      (Satellite)            │  │
│   ├─────────────────┤         ├─────────────────────────────┤  │
│   │ - SSO Central   │◄───────►│ - Frontend Next.js (3002)   │  │
│   │ - Billing       │  JWT    │ - Backend FastAPI (8002)    │  │
│   │ - User Mgmt     │         │ - Chat IA / Brief Gen       │  │
│   │ Port: 3000/8000 │         │ - Site Renderer             │  │
│   └─────────────────┘         └─────────────────────────────┘  │
│                                                                 │
│   Réseau Docker: dc360-ecosystem-net                           │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Stack Technique

| Composant | Technologie |
|-----------|-------------|
| **Frontend** | Next.js 14+ / TypeScript / Tailwind CSS |
| **Backend** | FastAPI / Python 3.12 / Pydantic |
| **Auth** | JWT (SSO via DC360 Hub) |
| **Database** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **Containerisation** | Docker / Docker Compose |

---

## 2. Périmètre de Travail Actuel

### 2.1 Mission Immédiate : Finaliser SSO Token Passing

**Objectif** : Permettre à un utilisateur authentifié sur DC360 Hub d'accéder à Genesis sans re-login.

**Flux SSO** :
```
1. User sur DC360 Hub (localhost:3000) → Clic "Accéder à Genesis"
2. Redirect vers Genesis (localhost:3002?token=JWT_TOKEN)
3. Genesis extrait le token de l'URL
4. Genesis valide le token auprès de DC360
5. Genesis stocke le token en cookie
6. Genesis nettoie l'URL (sécurité)
7. User redirigé vers /chat (authentifié)
```

**Fichiers concernés** :
- `genesis-frontend/src/context/AuthContext.tsx` ✅ (déjà implémenté)
- `genesis-frontend/src/app/api/auth/validate/route.ts` ❌ **À CRÉER**

### 2.2 Tâche Critique : Créer l'endpoint `/api/auth/validate`

Ce fichier **n'existe pas** et bloque le SSO.

**Spécifications** :

```typescript
// genesis-frontend/src/app/api/auth/validate/route.ts

import { NextRequest, NextResponse } from 'next/server';

const DC360_API_URL = process.env.DC360_API_URL || 'http://web:8000/api';

export async function POST(request: NextRequest) {
    try {
        const { token } = await request.json();

        if (!token) {
            return NextResponse.json(
                { error: 'Token manquant' },
                { status: 400 }
            );
        }

        // Valider le token auprès de DC360 Hub
        const response = await fetch(`${DC360_API_URL}/auth/user/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            return NextResponse.json(
                { error: 'Token invalide' },
                { status: 401 }
            );
        }

        const userData = await response.json();

        return NextResponse.json(userData, { status: 200 });

    } catch (error) {
        console.error('Erreur validation token:', error);
        return NextResponse.json(
            { error: 'Erreur serveur' },
            { status: 500 }
        );
    }
}
```

### 2.3 Correction Docker Recommandée

Le service `genesis-api` doit aussi être sur le réseau `dc360-ecosystem-net` pour permettre la communication frontend → backend.

**Dans `docker-compose.yml`**, ajouter au service `genesis-api` :
```yaml
networks:
  - genesis-ai-network
  - dc360-ecosystem-net  # AJOUTER CETTE LIGNE
```

---

## 3. Règles de Sécurité - OBLIGATOIRES

### 3.1 Security by Design - Les 3 Principes Fondamentaux

#### Principe 1 : "The Token is the Truth"
> L'identité de l'utilisateur vient **uniquement** du token JWT décodé côté backend.

- ❌ **INTERDIT** : Envoyer `userId` dans le body d'une requête
- ❌ **INTERDIT** : Faire confiance à un ID venant du frontend
- ✅ **OBLIGATOIRE** : Extraire l'identité depuis le token JWT côté serveur

```typescript
// ❌ MAUVAIS
fetch('/api/chat', {
    body: JSON.stringify({ userId: 123, message: '...' })
});

// ✅ BON
fetch('/api/chat', {
    headers: { 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ message: '...' })
});
```

#### Principe 2 : "Chain of Trust"
> Chaque maillon de la chaîne doit propager le token sans le modifier.

```
Frontend → API Route Next.js → Backend FastAPI → Service
    │              │                  │
    └── Token ─────┴─── Token ────────┘
```

- Le frontend envoie le token dans le header `Authorization`
- L'API Route Next.js **propage** ce header au backend
- Le backend valide et extrait l'identité

#### Principe 3 : "Zero Trust Input"
> Ne jamais faire confiance aux données venant du client.

- Valider **toutes** les entrées avec Pydantic (backend) ou Zod (frontend)
- Utiliser `extra="forbid"` dans les modèles Pydantic pour rejeter les champs inconnus
- Échapper les données avant affichage (XSS)

### 3.2 Gestion des Cookies

```typescript
// ✅ Cookie sécurisé
document.cookie = `access_token=${token}; path=/; max-age=86400; SameSite=Lax`;

// En production, ajouter :
// - Secure (HTTPS uniquement)
// - HttpOnly (si possible via Set-Cookie serveur)
```

### 3.3 Nettoyage de l'URL

Après extraction du token, **toujours** nettoyer l'URL :

```typescript
// ✅ Nettoyer l'URL pour ne pas exposer le token
window.history.replaceState({}, '', window.location.pathname);
```

Cela évite :
- Token visible dans la barre d'adresse
- Token dans l'historique du navigateur
- Token partagé accidentellement (copier-coller URL)

---

## 4. Bonnes Pratiques de Développement

### 4.1 Git Workflow

```bash
# 1. Toujours partir de master à jour
git checkout master
git pull origin master

# 2. Créer une branche feature dédiée
git checkout -b feature/nom-de-la-feature

# 3. Commits atomiques et bien nommés
git commit -m "feat(auth): add /api/auth/validate endpoint"
git commit -m "fix(docker): add genesis-api to dc360-ecosystem-net"

# 4. Push et PR
git push origin feature/nom-de-la-feature
# Créer une PR sur GitHub
```

**Convention de commits** :
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `refactor:` refactoring sans changement fonctionnel
- `test:` ajout/modification de tests

### 4.2 Environnement Docker

```bash
# Lancer l'environnement complet
docker compose up -d

# Rebuild après modification de code
docker compose build --no-cache frontend
docker compose up -d frontend

# Voir les logs
docker compose logs -f frontend
docker compose logs -f genesis-api

# Accès aux services
# - Genesis Frontend : http://localhost:3002
# - Genesis API : http://localhost:8002
# - DC360 Hub : http://localhost:3000 (si lancé séparément)
```

### 4.3 Structure des Fichiers Frontend

```
genesis-frontend/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth/
│   │   │   │   ├── me/route.ts       # GET user info
│   │   │   │   └── validate/route.ts # POST validate token ← À CRÉER
│   │   │   └── chat/route.ts         # POST chat message
│   │   ├── chat/page.tsx             # Page chat
│   │   ├── page.tsx                  # Landing page
│   │   └── layout.tsx                # Layout principal
│   ├── components/
│   │   └── ChatInterface.tsx         # Composant chat
│   ├── context/
│   │   └── AuthContext.tsx           # Context auth (SSO)
│   └── lib/
│       └── auth.ts                   # Helpers auth
├── Dockerfile
└── .env.local
```

---

## 5. Ressources et Documentation

### 5.1 Work Orders de Référence

| Document | Chemin |
|----------|--------|
| WO Homepage | `docs/work_order/WO-GENESIS-FRONTEND-HOMEPAGE-IMPLEMENTATION.md` |
| WO SSO Token Passing | `docs/work_order/WO-GENESIS-SSO-TOKEN-PASSING.md` |
| WO Backend Chat API | `docs/work_order/WO-GENESIS-BACKEND-CHAT-API.md` |

### 5.2 Memos Importants

| Document | Chemin |
|----------|--------|
| Vision Genesis AI | `docs/memo/MEMO_PROPOSAL_GENESIS_AI_PARTNER_VISION_27_11_2025.md` |
| Architecture Satellite | `docs/memo/MEMO_RESPONSE_ARCHITECTURE_GENESIS_SATELLITE.md` |
| Config Réseau E2E | `docs/memo/MEMO_REPONSE_CONFIG_RESEAU_E2E_27_11_2025.md` |

### 5.3 Contacts

- **Tech Lead Genesis AI** : Cascade (coordination technique, review PR)
- **Product Owner** : Validation finale des livrables

---

## 6. Checklist de Démarrage

- [ ] Cloner le repo : `git clone https://github.com/digitalcigit/digitalcloud360_generis.git`
- [ ] Se positionner sur la branche de travail : `git checkout feature/frontend-homepage`
- [ ] Copier `.env.example` vers `.env` et configurer les variables
- [ ] Lancer Docker : `docker compose up -d`
- [ ] Vérifier que le frontend répond : `http://localhost:3002`
- [ ] Lire ce mémo en entier
- [ ] Créer l'endpoint `/api/auth/validate/route.ts`
- [ ] Tester le flux SSO complet
- [ ] Commit + Push + Notifier le Tech Lead

---

## 7. Definition of Done (DoD)

Ta mission est **terminée** quand :

1. ✅ L'endpoint `/api/auth/validate` existe et fonctionne
2. ✅ Le flux SSO complet est fonctionnel (DC360 → Genesis → /chat)
3. ✅ Le token est stocké en cookie avec `SameSite=Lax`
4. ✅ L'URL est nettoyée après extraction du token
5. ✅ Le code respecte les principes Security by Design
6. ✅ Les modifications sont commitées et poussées sur GitHub
7. ✅ Le Tech Lead a validé la PR

---

Bienvenue dans l'équipe ! N'hésite pas à poser des questions si quelque chose n'est pas clair.

---
_Tech Lead Genesis AI_
