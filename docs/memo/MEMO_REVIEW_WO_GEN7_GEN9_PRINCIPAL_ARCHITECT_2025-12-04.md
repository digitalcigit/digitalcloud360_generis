# 📋 Mémo Review — WO GEN-7 & GEN-9

**Date :** 2025-12-04  
**De :** Principal Architect & Ecosystem Scrum Master DC360  
**À :** Tech Lead Genesis AI  
**Objet :** Double-check des Work Orders GEN-7 (Transformer) et GEN-9 (Block Renderer)

---

## 1. Contexte

À la demande du PO, j'ai effectué une revue approfondie des deux Work Orders :
- **WO GEN-7** : Transformer (Brief → SiteDefinition)
- **WO GEN-9** : Block Renderer (Composants React)

**Verdict global :** Les deux WO sont de **très bonne qualité**, bien structurés et actionnables. Cependant, j'ai identifié **un problème de cohérence critique** à résoudre avant transmission aux devs.

---

## 2. 🚨 Problème Critique : Désalignement des Props

### 2.1 Constat

Il y a une incohérence entre les noms de propriétés utilisés :

| Source | Hero Props | CTA Props |
|--------|------------|-----------|
| **Code actuel** (`app/services/transformer.py`) | `title`, `subtitle`, `cta.link` | ✅ |
| **WO GEN-7** (test L331-338) | `title`, `subtitle`, `cta.link` | ✅ Aligné sur existant |
| **WO GEN-8** (schema livré) | `headline`, `subheadline`, `ctaButtons[].href` | ❓ À confirmer |
| **WO GEN-9** (`CTABlock.tsx`) | `headline`, `primaryButton.href` | Suit GEN-8 |

### 2.2 Impact

Si le schema GEN-8 utilise `headline`/`subheadline` :
1. **GEN-7 Transformer** génère `title`, `subtitle` (actuel)
2. **GEN-9 Renderer** attend `headline`, `subheadline` (du schema)
3. ➡️ **Incompatibilité** : le JSON produit ne sera pas rendu correctement

### 2.3 Question

**Quel naming a été retenu dans le schema GEN-8 final ?**

- **Option A** : `title`, `subtitle`, `cta.link` (aligné sur code existant)
- **Option B** : `headline`, `subheadline`, `ctaButtons[].href` (WO original)

Une fois confirmé, l'autre WO (GEN-7 ou GEN-9) doit être mis à jour pour garantir la cohérence.

---

## 3. Points Forts (à conserver)

### WO GEN-7 (Transformer)

| Aspect | Évaluation |
|--------|------------|
| Section **Non-Objectives** | ✅ Excellent — scope clair |
| Specs **Input/Output** | ✅ Bien documentés |
| **Mapping sectoriel** (`sector_mappings.py`) | ✅ Très pertinent |
| **Tests unitaires** (6 tests) | ✅ Couverture correcte |
| **Workflow Git** | ✅ Conforme aux conventions |

### WO GEN-9 (Block Renderer)

| Aspect | Évaluation |
|--------|------------|
| **Dynamic imports** (`next/dynamic`) | ✅ Code splitting optimal |
| **ThemeProvider** avec CSS variables | ✅ Approche moderne |
| Architecture **PageRenderer + SiteRenderer** | ✅ Hiérarchie propre |
| **Composants complets** | ✅ Prêts à implémenter |

---

## 4. Points à Améliorer

### 4.1 WO GEN-7

| # | Point | Priorité | Suggestion |
|---|-------|----------|------------|
| 1 | **Validation Pydantic manquante** | 🟠 Important | Ajouter `SiteDefinition(**site_dict)` pour valider l'output |
| 2 | Import `BlockType` non utilisé | 🟡 Mineur | Retirer ou utiliser dans un test |
| 3 | Estimation serrée (10-12h) | 🟡 Mineur | Ajouter buffer ou noter "hors scope : briefs incomplets" |

**Suggestion de code pour validation :**

```python
from app.schemas.site_definition import SiteDefinition

def transform(self, brief: BusinessBrief) -> Dict[str, Any]:
    site_dict = { ... }
    # Valider avant de retourner
    SiteDefinition(**site_dict)  # Lève ValidationError si invalide
    return site_dict
```

### 4.2 WO GEN-9

| # | Point | Priorité | Suggestion |
|---|-------|----------|------------|
| 1 | **HeaderBlock ambigu** | 🟠 Important | Clarifier : inclus ou stretch goal ? |
| 2 | **Icons en texte brut** | 🟡 Mineur | Préciser : Lucide, emojis, ou CSS classes ? |
| 3 | Form submission non implémenté | 🟡 Mineur | Ajouter dans Non-Objectives |
| 4 | **Tests absents** | 🟢 Optionnel | Ajouter test de smoke minimal |

**Suggestion pour HeaderBlock :**

```markdown
## 2.1 Non-Objectifs (Hors Scope GEN-9)

- ❌ HeaderBlock (sera traité en Phase 2 si navigation multi-pages)
- ❌ Logique d'envoi du formulaire contact (Phase 2)
```

**Suggestion pour test de smoke :**

```typescript
// __tests__/components/BlockRenderer.test.tsx
import { render } from '@testing-library/react';
import BlockRenderer from '@/components/BlockRenderer';

const mockSections = {
  hero: { id: '1', type: 'hero', content: { title: 'Test', subtitle: 'Sub' } },
  // ... autres types
};

describe('BlockRenderer', () => {
  Object.entries(mockSections).forEach(([type, section]) => {
    it(`renders ${type} without crashing`, () => {
      expect(() => render(<BlockRenderer section={section} />)).not.toThrow();
    });
  });
});
```

---

## 5. Tableau Récapitulatif des Actions

| # | WO | Action | Priorité | Status |
|---|-----|--------|----------|--------|
| 1 | **GEN-7 & GEN-9** | Aligner props Hero (`title` vs `headline`) | 🔴 Critique | ⏳ En attente réponse |
| 2 | GEN-7 | Ajouter validation Pydantic dans `transform()` | 🟠 Important | À faire |
| 3 | GEN-9 | Clarifier scope HeaderBlock | 🟠 Important | À faire |
| 4 | GEN-9 | Préciser gestion des icônes | 🟡 Mineur | À faire |
| 5 | GEN-9 | Ajouter "form submission" dans Non-Objectives | 🟡 Mineur | À faire |
| 6 | GEN-9 | Ajouter test de smoke basique | 🟢 Optionnel | Suggestion |

---

## 6. Questions pour le Tech Lead

1. **Props Hero :** Le schema GEN-8 final utilise-t-il `title`/`subtitle` ou `headline`/`subheadline` ?

2. **HeaderBlock :** Doit-il être inclus dans GEN-9 ou reporté à Phase 2 ?

3. **Icons :** Quelle solution pour les icônes ? (Lucide, emojis, SVG inline ?)

4. **Tests GEN-9 :** Faut-il ajouter des tests dans le scope, ou les reporter à GEN-11 ?

---

## 7. Prochaines Étapes

1. **Tech Lead** confirme le naming des props (question 1)
2. **Tech Lead** met à jour les WO concernés
3. **Principal Architect** valide les WO finaux
4. **Transmission aux devs** avec scope clarifié

---

**En attente de ton retour sur les questions ci-dessus.**

*— Principal Architect & Ecosystem Scrum Master DC360*
