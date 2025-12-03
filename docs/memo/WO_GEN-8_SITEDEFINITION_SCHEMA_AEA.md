# 📋 Work Order — GEN-8 : SiteDefinition Schema

**Date :** 2025-12-03  
**De :** Tech Lead Genesis AI (Cascade)  
**À :** DCI DEV - AEA (`agnissan@digital.ci`)  
**Objet :** Implémentation complète du SiteDefinition JSON Schema

---

## 1. Contexte

Tu es assigné à la story **GEN-8 : SiteDefinition JSON Schema**, qui est la **fondation** de tout le Sprint 5. Les autres stories (GEN-7, GEN-9, etc.) dépendent de ce travail.

### Objectif
Définir le schéma complet `SiteDefinition` avec tous les types de blocks (sections) nécessaires pour rendre un site web généré par Genesis AI.

### Liens de Suivi

| Outil | Lien / ID |
|-------|-----------|
| **Asana** | Task GID `1212242789315035` |
| **Jira** | [GEN-8](https://digitalcloud360.atlassian.net/browse/GEN-8) |
| **Projet Asana** | Genesis (`1212238584177337`) |

**⚠️ IMPORTANT :** Mets à jour Asana au fur et à mesure que tu complètes les sous-tâches.

---

## 2. Deadline & Estimation

| Métrique | Valeur |
|----------|--------|
| **Deadline** | **03/12/2025** (aujourd'hui) |
| **Estimation** | 6-7h |
| **Priorité** | 🔴 Highest |

---

## 3. État Actuel du Code

### Frontend (`genesis-frontend/src/types/`)

**Fichier existant :** `site-definition.ts` (35 lignes - basique)

```typescript
// État actuel - À AMÉLIORER
export interface SiteSection {
  id: string;
  type: string;  // ⚠️ Trop générique ! Doit être une union stricte
  content: Record<string, any>;  // ⚠️ Pas typé ! Doit être spécifique par block
  styles?: Record<string, any>;
}
```

**Problème :** Le `type` est un `string` générique et `content` est `Record<string, any>`. On perd tout le typage fort.

### Backend (`app/schemas/`)

**Fichier à créer :** `site_definition.py` (n'existe pas encore)

**Pattern à suivre :** Voir `app/schemas/business.py` pour le style Pydantic avec `Field`, descriptions et examples.

### Blocks React existants (`genesis-frontend/src/components/blocks/`)

| Block | Status |
|-------|--------|
| `HeroBlock.tsx` | ✅ Existe |
| `FeaturesBlock.tsx` | ✅ Existe |
| `FooterBlock.tsx` | ✅ Existe |
| `AboutBlock.tsx` | ❌ À créer (GEN-9) |
| `ServicesBlock.tsx` | ❌ À créer (GEN-9) |
| `ContactBlock.tsx` | ❌ À créer (GEN-9) |
| `TestimonialsBlock.tsx` | ❌ À créer (GEN-9) |
| `GalleryBlock.tsx` | ❌ À créer (GEN-9) |
| `CTABlock.tsx` | ❌ À créer (GEN-9) |

---

## 4. Sous-Tâches Asana (Mapping)

Voici le mapping entre les sous-tâches Asana et le travail à faire :

| # | Sous-tâche Asana | Fichier à créer/modifier | Estimation |
|---|------------------|--------------------------|------------|
| 1 | `Définir tous les block types` | `src/types/site-definition.ts` | 1h |
| 2 | `Typer HeroSectionContent` | `src/types/blocks/hero.ts` | 0.5h |
| 3 | `Typer ServicesSectionContent` | `src/types/blocks/services.ts` | 0.5h |
| 4 | `Typer AboutSectionContent` | `src/types/blocks/about.ts` | 0.5h |
| 5 | `Typer FeaturesSectionContent` | `src/types/blocks/features.ts` | 0.5h |
| 6 | `Typer TestimonialsSectionContent` | `src/types/blocks/testimonials.ts` | 0.5h |
| 7 | `Typer GallerySectionContent` | `src/types/blocks/gallery.ts` | 0.5h |
| 8 | `Typer CTASectionContent` | `src/types/blocks/cta.ts` | 0.5h |
| 9 | `Typer ContactSectionContent` | `src/types/blocks/contact.ts` | 0.5h |
| 10 | `Typer FooterSectionContent` | `src/types/blocks/footer.ts` | 0.5h |
| 11 | `Créer index barrel export` | `src/types/blocks/index.ts` | 0.5h |
| 12 | `Créer Pydantic schema miroir (backend)` | `app/schemas/site_definition.py` | 1h |

---

## 5. Spécifications Techniques

### 5.1 Structure des Dossiers à Créer

```
genesis-frontend/src/types/
├── site-definition.ts      # MODIFIER - Ajouter BlockType union + BlockContentMap
└── blocks/                  # CRÉER ce dossier
    ├── index.ts             # Barrel export
    ├── hero.ts
    ├── about.ts
    ├── services.ts
    ├── features.ts
    ├── testimonials.ts
    ├── contact.ts
    ├── gallery.ts
    ├── cta.ts
    └── footer.ts

app/schemas/
└── site_definition.py       # CRÉER - Pydantic mirror
```

### 5.2 Types TypeScript à Implémenter

#### `src/types/site-definition.ts` (MODIFIER)

```typescript
// ===== BLOCK TYPES =====
export type BlockType = 
  | 'hero' 
  | 'about' 
  | 'services' 
  | 'features' 
  | 'testimonials' 
  | 'contact' 
  | 'gallery' 
  | 'cta' 
  | 'footer';

// ===== BLOCK CONTENT MAP =====
export interface BlockContentMap {
  hero: HeroSectionContent;
  about: AboutSectionContent;
  services: ServicesSectionContent;
  features: FeaturesSectionContent;
  testimonials: TestimonialsSectionContent;
  contact: ContactSectionContent;
  gallery: GallerySectionContent;
  cta: CTASectionContent;
  footer: FooterSectionContent;
}

// ===== SECTION GÉNÉRIQUE TYPÉE =====
export interface SiteSection<T extends BlockType = BlockType> {
  id: string;
  type: T;
  content: BlockContentMap[T];
  styles?: SectionStyles;
}

// ===== STYLES =====
export interface SectionStyles {
  backgroundColor?: string;
  padding?: string;
  margin?: string;
  className?: string;
}

// ===== SITE DEFINITION =====
export interface SiteDefinition {
  metadata: SiteMetadata;
  theme: SiteTheme;
  pages: SitePage[];
}

export interface SiteMetadata {
  title: string;
  description: string;
  favicon?: string;
  ogImage?: string;
}

export interface SiteTheme {
  colors: ThemeColors;
  fonts: ThemeFonts;
}

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent?: string;
  background: string;
  text: string;
}

export interface ThemeFonts {
  heading: string;
  body: string;
}

export interface SitePage {
  id: string;
  slug: string;
  title: string;
  sections: SiteSection[];
}

// ===== IMPORTS DES BLOCK CONTENTS =====
export * from './blocks';
```

#### `src/types/blocks/hero.ts`

```typescript
export interface HeroSectionContent {
  headline: string;
  subheadline?: string;
  description?: string;
  backgroundImage?: string;
  backgroundVideo?: string;
  ctaButtons?: HeroCTA[];
  alignment?: 'left' | 'center' | 'right';
  overlay?: boolean;
}

export interface HeroCTA {
  text: string;
  href: string;
  variant?: 'primary' | 'secondary' | 'outline';
}
```

#### `src/types/blocks/about.ts`

```typescript
export interface AboutSectionContent {
  title: string;
  subtitle?: string;
  description: string;
  mission?: string;
  vision?: string;
  image?: string;
  stats?: AboutStat[];
}

export interface AboutStat {
  value: string;
  label: string;
}
```

#### `src/types/blocks/services.ts`

```typescript
export interface ServicesSectionContent {
  title: string;
  subtitle?: string;
  services: ServiceItem[];
  layout?: 'grid' | 'list' | 'cards';
}

export interface ServiceItem {
  id: string;
  title: string;
  description: string;
  icon?: string;
  image?: string;
  price?: string;
  href?: string;
}
```

#### `src/types/blocks/features.ts`

```typescript
export interface FeaturesSectionContent {
  title: string;
  subtitle?: string;
  features: FeatureItem[];
  layout?: 'grid' | 'alternating' | 'centered';
}

export interface FeatureItem {
  id: string;
  title: string;
  description: string;
  icon?: string;
  image?: string;
}
```

#### `src/types/blocks/testimonials.ts`

```typescript
export interface TestimonialsSectionContent {
  title: string;
  subtitle?: string;
  testimonials: TestimonialItem[];
  layout?: 'carousel' | 'grid' | 'masonry';
}

export interface TestimonialItem {
  id: string;
  quote: string;
  author: string;
  role?: string;
  company?: string;
  avatar?: string;
  rating?: number;
}
```

#### `src/types/blocks/contact.ts`

```typescript
export interface ContactSectionContent {
  title: string;
  subtitle?: string;
  description?: string;
  email?: string;
  phone?: string;
  address?: ContactAddress;
  socialLinks?: SocialLink[];
  showForm?: boolean;
  formFields?: ContactFormField[];
  mapEmbed?: string;
}

export interface ContactAddress {
  street: string;
  city: string;
  country: string;
  postalCode?: string;
}

export interface SocialLink {
  platform: 'facebook' | 'twitter' | 'instagram' | 'linkedin' | 'youtube' | 'tiktok';
  url: string;
}

export interface ContactFormField {
  name: string;
  type: 'text' | 'email' | 'tel' | 'textarea';
  label: string;
  required?: boolean;
  placeholder?: string;
}
```

#### `src/types/blocks/gallery.ts`

```typescript
export interface GallerySectionContent {
  title?: string;
  subtitle?: string;
  images: GalleryImage[];
  layout?: 'grid' | 'masonry' | 'carousel';
  columns?: 2 | 3 | 4;
}

export interface GalleryImage {
  id: string;
  src: string;
  alt: string;
  caption?: string;
  href?: string;
}
```

#### `src/types/blocks/cta.ts`

```typescript
export interface CTASectionContent {
  headline: string;
  description?: string;
  primaryButton: CTAButton;
  secondaryButton?: CTAButton;
  backgroundColor?: string;
  backgroundImage?: string;
}

export interface CTAButton {
  text: string;
  href: string;
  variant?: 'primary' | 'secondary' | 'outline';
}
```

#### `src/types/blocks/footer.ts`

```typescript
export interface FooterSectionContent {
  logo?: string;
  companyName: string;
  description?: string;
  columns?: FooterColumn[];
  copyright?: string;
  socialLinks?: SocialLink[];
  legalLinks?: FooterLink[];
}

export interface FooterColumn {
  title: string;
  links: FooterLink[];
}

export interface FooterLink {
  text: string;
  href: string;
}

// Réutiliser SocialLink de contact.ts
export type { SocialLink } from './contact';
```

#### `src/types/blocks/index.ts` (Barrel Export)

```typescript
// Block Contents
export * from './hero';
export * from './about';
export * from './services';
export * from './features';
export * from './testimonials';
export * from './contact';
export * from './gallery';
export * from './cta';
export * from './footer';
```

### 5.3 Schema Pydantic Backend

#### `app/schemas/site_definition.py`

```python
"""SiteDefinition Pydantic schemas - Miroir des types TypeScript frontend"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Union
from enum import Enum


# ===== BLOCK TYPES =====
class BlockType(str, Enum):
    HERO = "hero"
    ABOUT = "about"
    SERVICES = "services"
    FEATURES = "features"
    TESTIMONIALS = "testimonials"
    CONTACT = "contact"
    GALLERY = "gallery"
    CTA = "cta"
    FOOTER = "footer"


# ===== HERO =====
class HeroCTA(BaseModel):
    text: str
    href: str
    variant: Optional[Literal["primary", "secondary", "outline"]] = "primary"


class HeroSectionContent(BaseModel):
    headline: str = Field(..., description="Titre principal du hero")
    subheadline: Optional[str] = None
    description: Optional[str] = None
    backgroundImage: Optional[str] = None
    backgroundVideo: Optional[str] = None
    ctaButtons: Optional[List[HeroCTA]] = None
    alignment: Optional[Literal["left", "center", "right"]] = "center"
    overlay: Optional[bool] = False


# ===== ABOUT =====
class AboutStat(BaseModel):
    value: str
    label: str


class AboutSectionContent(BaseModel):
    title: str = Field(..., description="Titre de la section À propos")
    subtitle: Optional[str] = None
    description: str
    mission: Optional[str] = None
    vision: Optional[str] = None
    image: Optional[str] = None
    stats: Optional[List[AboutStat]] = None


# ===== SERVICES =====
class ServiceItem(BaseModel):
    id: str
    title: str
    description: str
    icon: Optional[str] = None
    image: Optional[str] = None
    price: Optional[str] = None
    href: Optional[str] = None


class ServicesSectionContent(BaseModel):
    title: str = Field(..., description="Titre de la section Services")
    subtitle: Optional[str] = None
    services: List[ServiceItem]
    layout: Optional[Literal["grid", "list", "cards"]] = "grid"


# ===== FEATURES =====
class FeatureItem(BaseModel):
    id: str
    title: str
    description: str
    icon: Optional[str] = None
    image: Optional[str] = None


class FeaturesSectionContent(BaseModel):
    title: str = Field(..., description="Titre de la section Features")
    subtitle: Optional[str] = None
    features: List[FeatureItem]
    layout: Optional[Literal["grid", "alternating", "centered"]] = "grid"


# ===== TESTIMONIALS =====
class TestimonialItem(BaseModel):
    id: str
    quote: str
    author: str
    role: Optional[str] = None
    company: Optional[str] = None
    avatar: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class TestimonialsSectionContent(BaseModel):
    title: str = Field(..., description="Titre de la section Testimonials")
    subtitle: Optional[str] = None
    testimonials: List[TestimonialItem]
    layout: Optional[Literal["carousel", "grid", "masonry"]] = "grid"


# ===== CONTACT =====
class ContactAddress(BaseModel):
    street: str
    city: str
    country: str
    postalCode: Optional[str] = None


class SocialLink(BaseModel):
    platform: Literal["facebook", "twitter", "instagram", "linkedin", "youtube", "tiktok"]
    url: str


class ContactFormField(BaseModel):
    name: str
    type: Literal["text", "email", "tel", "textarea"]
    label: str
    required: Optional[bool] = False
    placeholder: Optional[str] = None


class ContactSectionContent(BaseModel):
    title: str = Field(..., description="Titre de la section Contact")
    subtitle: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[ContactAddress] = None
    socialLinks: Optional[List[SocialLink]] = None
    showForm: Optional[bool] = True
    formFields: Optional[List[ContactFormField]] = None
    mapEmbed: Optional[str] = None


# ===== GALLERY =====
class GalleryImage(BaseModel):
    id: str
    src: str
    alt: str
    caption: Optional[str] = None
    href: Optional[str] = None


class GallerySectionContent(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    images: List[GalleryImage]
    layout: Optional[Literal["grid", "masonry", "carousel"]] = "grid"
    columns: Optional[Literal[2, 3, 4]] = 3


# ===== CTA =====
class CTAButton(BaseModel):
    text: str
    href: str
    variant: Optional[Literal["primary", "secondary", "outline"]] = "primary"


class CTASectionContent(BaseModel):
    headline: str = Field(..., description="Titre du CTA")
    description: Optional[str] = None
    primaryButton: CTAButton
    secondaryButton: Optional[CTAButton] = None
    backgroundColor: Optional[str] = None
    backgroundImage: Optional[str] = None


# ===== FOOTER =====
class FooterLink(BaseModel):
    text: str
    href: str


class FooterColumn(BaseModel):
    title: str
    links: List[FooterLink]


class FooterSectionContent(BaseModel):
    logo: Optional[str] = None
    companyName: str = Field(..., description="Nom de l'entreprise")
    description: Optional[str] = None
    columns: Optional[List[FooterColumn]] = None
    copyright: Optional[str] = None
    socialLinks: Optional[List[SocialLink]] = None
    legalLinks: Optional[List[FooterLink]] = None


# ===== SECTION CONTENT UNION =====
SectionContent = Union[
    HeroSectionContent,
    AboutSectionContent,
    ServicesSectionContent,
    FeaturesSectionContent,
    TestimonialsSectionContent,
    ContactSectionContent,
    GallerySectionContent,
    CTASectionContent,
    FooterSectionContent
]


# ===== SITE SECTION =====
class SectionStyles(BaseModel):
    backgroundColor: Optional[str] = None
    padding: Optional[str] = None
    margin: Optional[str] = None
    className: Optional[str] = None


class SiteSection(BaseModel):
    id: str
    type: BlockType
    content: SectionContent
    styles: Optional[SectionStyles] = None


# ===== SITE STRUCTURE =====
class SiteMetadata(BaseModel):
    title: str = Field(..., description="Titre du site")
    description: str = Field(..., description="Meta description")
    favicon: Optional[str] = None
    ogImage: Optional[str] = None


class ThemeColors(BaseModel):
    primary: str = Field(..., description="Couleur primaire (hex)")
    secondary: str = Field(..., description="Couleur secondaire (hex)")
    accent: Optional[str] = None
    background: str = "#ffffff"
    text: str = "#1a1a1a"


class ThemeFonts(BaseModel):
    heading: str = "Inter"
    body: str = "Inter"


class SiteTheme(BaseModel):
    colors: ThemeColors
    fonts: ThemeFonts


class SitePage(BaseModel):
    id: str
    slug: str = Field(..., description="URL slug de la page (ex: / pour homepage)")
    title: str
    sections: List[SiteSection]


class SiteDefinition(BaseModel):
    """Schema complet d'un site généré par Genesis AI"""
    metadata: SiteMetadata
    theme: SiteTheme
    pages: List[SitePage]
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "title": "TechStartup Dakar",
                    "description": "Solutions tech pour PME africaines"
                },
                "theme": {
                    "colors": {
                        "primary": "#2563eb",
                        "secondary": "#7c3aed",
                        "background": "#ffffff",
                        "text": "#1a1a1a"
                    },
                    "fonts": {"heading": "Inter", "body": "Inter"}
                },
                "pages": [{
                    "id": "home",
                    "slug": "/",
                    "title": "Accueil",
                    "sections": []
                }]
            }
        }
```

---

## 6. Workflow Git

### 6.1 Créer ta branche

```bash
cd c:\genesis
git checkout master
git pull origin master
git checkout -b feature/gen-8-sitedefinition-schema
```

### 6.2 Commits recommandés

```bash
# Après chaque groupe de fichiers
git add genesis-frontend/src/types/blocks/
git commit -m "feat(types): Add block type definitions for SiteDefinition"

git add genesis-frontend/src/types/site-definition.ts
git commit -m "feat(types): Extend SiteDefinition with BlockType union and BlockContentMap"

git add app/schemas/site_definition.py
git commit -m "feat(schema): Add Pydantic mirror for SiteDefinition"
```

### 6.3 Push et PR

```bash
git push origin feature/gen-8-sitedefinition-schema
```

Puis crée une **Pull Request** vers `master` avec :
- Titre : `feat(schema): [GEN-8] Complete SiteDefinition JSON Schema`
- Description : Liste les fichiers créés et mentionne les sous-tâches Asana complétées
- Reviewer : Tech Lead Genesis (Cascade)

---

## 7. Critères d'Acceptation

- [ ] **Frontend :** Tous les fichiers `src/types/blocks/*.ts` créés
- [ ] **Frontend :** `src/types/site-definition.ts` mis à jour avec `BlockType` union
- [ ] **Frontend :** `src/types/blocks/index.ts` barrel export fonctionnel
- [ ] **Backend :** `app/schemas/site_definition.py` créé
- [ ] **TypeScript :** Pas d'erreurs de compilation (`npm run build` ou `tsc --noEmit`)
- [ ] **Asana :** Toutes les sous-tâches marquées comme complétées
- [ ] **Git :** PR créée et prête pour review

---

## 8. Points de Contact

| Rôle | Contact | Pour |
|------|---------|------|
| **Tech Lead Genesis** | Cascade (via IDE) | Questions techniques, review PR |
| **Scrum Master** | Via Cascade | Clarifications fonctionnelles |

---

## 9. Ressources

| Document | Chemin |
|----------|--------|
| Brief Tech Lead Sprint 5 | `docs/memo/MEMO_BRIEF_TECH_LEAD_SPRINT5_2025-12-02.md` |
| Analyse technique Sprint 5 | `docs/Planning_Scrum/SUBTASKS_SPRINT5_TECH_ANALYSIS.md` |
| Schema existant business.py | `app/schemas/business.py` (pattern Pydantic) |
| Types existants | `genesis-frontend/src/types/site-definition.ts` |

---

## 10. Checklist Finale

Avant de soumettre ta PR, vérifie :

- [ ] Tu as créé le dossier `genesis-frontend/src/types/blocks/`
- [ ] Tu as créé les 9 fichiers de types de blocks
- [ ] Tu as créé le barrel export `index.ts`
- [ ] Tu as modifié `site-definition.ts` pour utiliser les nouveaux types
- [ ] Tu as créé `app/schemas/site_definition.py`
- [ ] `npm run build` passe sans erreur (si possible)
- [ ] Tu as mis à jour les sous-tâches Asana en "Completed"
- [ ] Tu as créé la PR avec un titre clair

---

**Bonne implémentation ! N'hésite pas à me ping si tu as des questions.**

*— Tech Lead Genesis AI (Cascade)*
