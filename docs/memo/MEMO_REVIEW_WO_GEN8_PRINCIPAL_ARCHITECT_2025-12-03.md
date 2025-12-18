# 📋 Mémo Review — WO GEN-8 SiteDefinition Schema

**Date :** 2025-12-03  
**De :** Principal Architect & Ecosystem Scrum Master DC360  
**À :** Tech Lead Genesis AI  
**Objet :** Revue approfondie du Work Order GEN-8 — Recommandations d'amélioration

---

## 1. Contexte

J'ai analysé en profondeur le Work Order `WO_GEN-8_SITEDEFINITION_SCHEMA_AEA.md` en le croisant avec :
- Le code existant (`site-definition.ts`, `BlockRenderer.tsx`, blocks React)
- Le brief Sprint 5 (`MEMO_BRIEF_TECH_LEAD_SPRINT5_2025-12-02.md`)
- Les patterns Pydantic du projet (`app/schemas/business.py`)
- Notre architecture validée (Hub & Satellites)

**Verdict global :** Le WO est de **très bonne qualité**, bien structuré et actionnable. Cependant, j'ai identifié **un problème critique** et plusieurs points d'amélioration.

---

## 2. 🚨 Problème Critique : Incompatibilité des Props

### 2.1 Constat

Les noms de champs proposés dans le WO **ne correspondent pas** aux props des composants React existants.

#### HeroBlock — BREAKING CHANGE

| Code actuel (`HeroBlock.tsx`) | WO proposé (`hero.ts`) |
|-------------------------------|------------------------|
| `title: string` | `headline: string` |
| `subtitle: string` | `subheadline?: string` |
| `image?: string` | `backgroundImage?: string` |
| `cta?: { text, link }` | `ctaButtons?: HeroCTA[]` avec `href` |

#### FooterBlock — Incohérence

| Code actuel | WO proposé |
|-------------|------------|
| `FooterLink.url` | `FooterLink.href` |

#### FeaturesBlock — Différence mineure

| Code actuel | WO proposé |
|-------------|------------|
| `Feature` sans `id` | `FeatureItem` avec `id: string` |

### 2.2 Impact

Le `BlockRenderer.tsx` actuel fait :
```typescript
case 'hero':
    return (
        <HeroBlock
            title={section.content.title}      // ← attend "title"
            subtitle={section.content.subtitle} // ← attend "subtitle"
            image={section.content.image}       // ← attend "image"
            cta={section.content.cta}           // ← attend "cta.link"
        />
    );
```

Si le dev GEN-8 implémente le schema avec `headline`, `subheadline`, `backgroundImage` :
- **Le TypeScript compile** (les types sont cohérents entre eux)
- **Mais le rendu est cassé** jusqu'à GEN-9 (refactoring des composants)

### 2.3 Options

#### Option A : Aligner le WO sur le code existant (RECOMMANDÉE)

Modifier le WO pour utiliser les noms existants :

```typescript
// hero.ts — VERSION ALIGNÉE
export interface HeroSectionContent {
    title: string;           // au lieu de "headline"
    subtitle?: string;       // au lieu de "subheadline"
    description?: string;
    image?: string;          // au lieu de "backgroundImage"
    backgroundVideo?: string;
    cta?: HeroCTA;           // single object, pas array
    alignment?: 'left' | 'center' | 'right';
    overlay?: boolean;
}

export interface HeroCTA {
    text: string;
    link: string;            // au lieu de "href"
    variant?: 'primary' | 'secondary' | 'outline';
}
```

**Avantage :** Le schema GEN-8 est immédiatement compatible. Le dev peut tester en local.

#### Option B : Garder le WO et documenter le breaking change

Si les noms du WO sont préférés (plus "standards" : `headline` > `title` pour un hero) :

1. Ajouter une section "Migration" listant les renommages nécessaires
2. Indiquer explicitement que GEN-9 doit migrer les composants
3. Accepter que le rendu soit cassé entre GEN-8 et GEN-9

---

## 3. Points d'Amélioration Supplémentaires

### 3.1 Tests Backend Manquants

Le brief Sprint 5 inclut :
> "Créer tests unitaires schema – `tests/schemas/test_site_definition.py`" (1.5h)

Le WO ne mentionne **aucun test**. Proposition d'ajout :

```markdown
## 5.4 Tests Backend

Créer `tests/schemas/test_site_definition.py` avec :

1. **Test happy path** — Création `SiteDefinition` valide avec l'exemple de `json_schema_extra`
2. **Test section Hero** — Validation du contenu typé
3. **Test validation rating** — `TestimonialItem.rating` doit être entre 1 et 5
4. **Test page sans sections** — Valider qu'une page vide est acceptée

Estimation : 1h
```

### 3.2 Section Non-Goals Absente

Ajouter pour clarifier le scope :

```markdown
## 2.1 Non-Objectifs (Hors Scope GEN-8)

- ❌ Modifier les composants React (`HeroBlock.tsx`, etc.)
- ❌ Modifier le `BlockRenderer.tsx`
- ❌ Créer de nouveaux blocks (scope GEN-9)
- ❌ Implémenter le Transformer (scope GEN-7)
- ❌ Créer des endpoints API (scope GEN-10)
```

### 3.3 Export dans `__init__.py`

Ajouter dans les sous-tâches :

```markdown
| 13 | Ajouter export dans `__init__.py` | `app/schemas/__init__.py` | 0.25h |
```

```python
# app/schemas/__init__.py — À ajouter
from .site_definition import (
    SiteDefinition,
    SiteSection,
    SitePage,
    SiteMetadata,
    SiteTheme,
    BlockType,
    # Block contents
    HeroSectionContent,
    AboutSectionContent,
    # ... etc
)
```

### 3.4 Source de Vérité

Ajouter une note architecturale :

```markdown
> **Note architecturale :** Pour Sprint 5, les types TypeScript et Pydantic sont maintenus 
> en synchronisation manuelle. À terme (Phase 2+), Pydantic/OpenAPI sera la source de vérité 
> et les types TS seront générés automatiquement via `openapi-typescript`.
```

### 3.5 Block Header/Navigation

Le WO définit 9 blocks mais pas de **Header/Navbar**. Pour un site complet, c'est nécessaire.

**Proposition :** Ajouter dans les types (même si le composant sera créé en GEN-9) :

```typescript
// header.ts
export interface HeaderSectionContent {
    logo?: string;
    companyName: string;
    navigation: NavItem[];
    ctaButton?: HeaderCTA;
    sticky?: boolean;
}

export interface NavItem {
    label: string;
    href: string;
    children?: NavItem[];
}
```

---

## 4. Points Forts du WO (à conserver)

| Aspect | Évaluation |
|--------|------------|
| Structure de dossiers (`src/types/blocks/`) | ✅ Excellent |
| Typage générique (`SiteSection<T extends BlockType>`) | ✅ Élégant |
| Barrel exports (`index.ts`) | ✅ Propre |
| Pydantic miroir avec `Field(description=...)` | ✅ Conforme au pattern projet |
| `json_schema_extra` avec example | ✅ Utile pour OpenAPI |
| Workflow Git détaillé | ✅ Clair |
| Critères d'acceptation explicites | ✅ Actionnable |

---

## 5. Tableau Récapitulatif des Actions

| # | Action | Priorité | Impact |
|---|--------|----------|--------|
| 1 | Aligner noms de props sur code existant | 🔴 Critique | Évite breaking change |
| 2 | Ajouter section Tests | 🟠 Important | Conforme au brief |
| 3 | Ajouter section Non-Goals | 🟠 Important | Clarifie le scope |
| 4 | Ajouter export `__init__.py` | 🟡 Mineur | Complétude |
| 5 | Ajouter note source de vérité | 🟡 Mineur | Documentation archi |
| 6 | Ajouter HeaderSectionContent | 🟢 Optionnel | Anticipation Phase 2 |

---

## 6. Questions pour le Tech Lead

1. **Props naming :** Préfères-tu aligner sur le code existant (`title`, `subtitle`, `image`) ou garder les noms "standards" du WO (`headline`, `subheadline`, `backgroundImage`) et migrer les composants en GEN-9 ?

2. **Tests :** Confirmes-tu qu'on doit inclure les tests dans GEN-8 comme indiqué dans le brief ?

3. **Header block :** Faut-il l'ajouter maintenant ou le garder pour une story ultérieure ?

4. **Deadline :** Avec ces ajouts, l'estimation passe de 6-7h à ~8h. Est-ce acceptable vu que la deadline est aujourd'hui (03/12) ?

---

## 7. Prochaines Étapes Proposées

1. **Tech Lead Genesis** analyse ce mémo et répond aux questions
2. **Mise à jour collaborative** du WO avec les corrections validées
3. **Transmission** du WO finalisé au dev AEA
4. **Suivi** de la PR par le Tech Lead

---

**En attente de ton retour pour finaliser le WO.**

*— Principal Architect & Ecosystem Scrum Master DC360*
