---
title: "MEMO: Clarification Flux /chat vs /coaching"
date: 2025-12-22
from: Cascade (Tech Lead Genesis)
to: Principal Architect
priority: HAUTE
type: clarification_architecture
status: action_requise
---

# 📋 MEMO: Clarification du Flux Utilisateur Genesis

## 1. Contexte

Suite à l'analyse du bug de "boucle infinie" sur la route `/chat`, une incohérence architecturale a été identifiée entre le code actuel et les décisions documentées.

## 2. Historique des Décisions (Work Orders)

| Date | Work Order | Décision |
|------|------------|----------|
| 19/12/2025 | **GEN-WO-001** | Flux Chat Intelligent maïeutique via `/chat` |
| 19/12/2025 | **GEN-WO-002** | Coaching 5 Étapes via `/coaching` — **REMPLACE GEN-WO-001** |
| 20/12/2025 | **GEN-WO-003** | Frontend `/coaching` — UI du coaching |
| 21/12/2025 | **GEN-WO-005** | Intégration Site Renderer `/coaching` → `/preview` |

### Point Critique
Dans `GEN-WO-002`, ligne 8 :
```yaml
supersedes: GEN-WO-001
```

**Le flux `/chat` a été officiellement remplacé par `/coaching`.**

## 3. Problème Identifié

### État Actuel du Code

| Route | Statut Officiel | Statut Code | Lien DC360 Hub |
|-------|-----------------|-------------|----------------|
| `/coaching` | ✅ **VALIDÉ** | ✅ Implémenté, fonctionnel | ❌ Non pointé |
| `/chat` | ❌ **REMPLACÉ** | ⚠️ Toujours présent | ⚠️ **Pointé (erreur)** |

### Conséquence
- L'utilisateur clique "Genesis" dans DC360 Hub → redirigé vers `/chat`
- `/chat` n'est plus maintenu → boucle d'authentification
- Pendant ce temps, `/coaching` fonctionne parfaitement

## 4. Flux Validé (Officiel)

```
DC360 Hub 
    │
    └──► Clic "Genesis" 
            │
            └──► /coaching (5 étapes maïeutiques)
                    │
                    └──► Génération LangGraph
                            │
                            └──► /preview/{sessionId}
```

## 5. Actions Requises

### Action 1 : Modifier DC360 Hub (PRIORITÉ HAUTE)
**Fichier à modifier** : Lien "Genesis" dans le Hub DC360

```diff
- href="http://localhost:3002/chat"
+ href="http://localhost:3002/coaching"
```

### Action 2 : Redirection de sécurité (OPTIONNEL)
Dans `genesis-frontend/src/app/chat/page.tsx`, ajouter une redirection :

```typescript
import { redirect } from 'next/navigation';

export default function ChatPage() {
    // Flux /chat remplacé par /coaching (GEN-WO-002)
    redirect('/coaching');
}
```

### Action 3 : Nettoyage futur (BASSE PRIORITÉ)
- Supprimer ou archiver la route `/chat`
- Mettre à jour la documentation

## 6. Validation Demandée

- [ ] Confirmer la modification du lien DC360 Hub
- [ ] Tester le flow complet : DC360 → `/coaching` → `/preview`
- [ ] Valider avec le PO

---

**Cascade, Tech Lead Genesis**
*22 Décembre 2025*
