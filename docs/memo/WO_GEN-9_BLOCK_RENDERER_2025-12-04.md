# 📋 Work Order — GEN-9 : Block Renderer (Composants React)

**Date :** 2025-12-04  
**De :** Tech Lead Genesis AI (Cascade)  
**À :** Développeur assigné  
**Objet :** Créer tous les composants React pour le rendu des blocks

---

## 1. Contexte

Le **Block Renderer** est le moteur de rendu frontend qui affiche les sites générés. Il reçoit un `SiteDefinition` JSON et rend les composants React correspondants pour chaque section.

### Liens de Suivi

| Outil | Lien / ID |
|-------|-----------|
| **Asana** | Task GID `1212242758897911` |
| **Jira** | [GEN-9](https://digitalcloud360.atlassian.net/browse/GEN-9) |
| **Dépendance** | GEN-8 ✅ (SiteDefinition Schema complété) |

---

## 2. Environnement de Développement (Docker)

Le projet tourne sous Docker. Pour développer les composants React :

1.  **Lancer le frontend :**
    ```bash
    cd c:\genesis
    docker-compose up -d frontend
    ```
    > L'app est accessible sur `http://localhost:3002`

2.  **Valider le code (dans le conteneur) :**
    ```bash
    docker-compose exec frontend npm run lint
    docker-compose exec frontend npm run build
    docker-compose exec frontend npm test
    ```

---

## 3. Deadline & Estimation

| Métrique | Valeur |
|----------|--------|
| **Deadline** | **09/12/2025** |
| **Estimation** | 12-14h |
| **Priorité** | 🔴 Highest |

### 2.1 Non-Objectifs (Hors Scope GEN-9)

> ⚠️ **Ne PAS faire dans cette story :**

- ❌ Implémenter le Transformer backend (scope GEN-7)
- ❌ Créer des endpoints API (scope GEN-10)
- ❌ Créer la page /preview (scope GEN-11)
- ❌ Animations avancées (Phase 2)
- ❌ Logique d'envoi du formulaire contact (UI seulement)

---

## 3. État Actuel du Code

### Composants existants : `genesis-frontend/src/components/blocks/`

| Composant | Status | Fichier |
|-----------|--------|---------|
| `HeroBlock.tsx` | ✅ Existe (basique) | À améliorer (props: `title`, `subtitle`) |
| `FeaturesBlock.tsx` | ✅ Existe | OK |
| `FooterBlock.tsx` | ✅ Existe (basique) | À améliorer |
| `AboutBlock.tsx` | ❌ Manque | À créer |
| `ServicesBlock.tsx` | ❌ Manque | À créer |
| `ContactBlock.tsx` | ❌ Manque | À créer |
| `TestimonialsBlock.tsx` | ❌ Manque | À créer |
| `GalleryBlock.tsx` | ❌ Manque | À créer |
| `CTABlock.tsx` | ❌ Manque | À créer |
| `HeaderBlock.tsx` | ❌ Manque | À créer (Implémentation basique) |

### Notes Techniques Importantes
- **Icônes** : Utiliser la librairie `lucide-react` déjà installée (ex: `<Users />`, `<Check />`).
- **Header** : Une version simple suffit pour cette phase (Logo + Nav Links + CTA).

### BlockRenderer existant

```typescript
// État actuel - Switch basique avec 3 cases
switch (section.type) {
    case 'hero': return <HeroBlock ... />;
    case 'features': return <FeaturesBlock ... />;
    case 'footer': return <FooterBlock ... />;
    default: return null;
}
```

### Types disponibles (GEN-8)

Les types TypeScript sont définis dans `src/types/blocks/*.ts` :
- `HeroSectionContent`, `AboutSectionContent`, `ServicesSectionContent`, etc.

---

## 4. Sous-Tâches Asana (Mapping)

| # | Sous-tâche Asana | Fichier | Estimation |
|---|------------------|---------|------------|
| 1 | Refactorer `BlockRenderer.tsx` avec map dynamique | `src/components/BlockRenderer.tsx` | 1h |
| 2 | Créer `AboutBlock.tsx` | `src/components/blocks/AboutBlock.tsx` | 1.5h |
| 3 | Créer `ServicesBlock.tsx` (grille de cards) | `src/components/blocks/ServicesBlock.tsx` | 2h |
| 4 | Créer `TestimonialsBlock.tsx` (carousel/grid) | `src/components/blocks/TestimonialsBlock.tsx` | 2h |
| 5 | Créer `ContactBlock.tsx` (formulaire) | `src/components/blocks/ContactBlock.tsx` | 2h |
| 6 | Créer `GalleryBlock.tsx` (grille images) | `src/components/blocks/GalleryBlock.tsx` | 1.5h |
| 7 | Créer `CTABlock.tsx` (call-to-action banner) | `src/components/blocks/CTABlock.tsx` | 1h |
| 8 | Améliorer `HeroBlock.tsx` (variants) | `src/components/blocks/HeroBlock.tsx` | 1h |
| 9 | Améliorer `FooterBlock.tsx` (colonnes, social) | `src/components/blocks/FooterBlock.tsx` | 1h |
| 10 | Créer `PageRenderer.tsx` | `src/components/PageRenderer.tsx` | 1h |
| 11 | Créer `SiteRenderer.tsx` | `src/components/SiteRenderer.tsx` | 1h |
| 12 | Support thème dynamique (CSS variables) | `src/components/ThemeProvider.tsx` | 1h |
| 13 | Ajouter Test Smoke (rendu sans crash) | `src/__tests__/components/BlockRenderer.test.tsx` | 1h |

---

## 5. Spécifications Techniques

### 5.1 Structure des Fichiers à Créer

```
genesis-frontend/src/components/
├── BlockRenderer.tsx        # REFACTORER - Map dynamique
├── PageRenderer.tsx         # CRÉER - Render une page complète
├── SiteRenderer.tsx         # CRÉER - Render multi-pages
├── ThemeProvider.tsx        # CRÉER - CSS variables dynamiques
└── blocks/
    ├── HeroBlock.tsx        # AMÉLIORER
    ├── FeaturesBlock.tsx    # OK
    ├── FooterBlock.tsx      # AMÉLIORER
    ├── AboutBlock.tsx       # CRÉER
    ├── ServicesBlock.tsx    # CRÉER
    ├── ContactBlock.tsx     # CRÉER
    ├── TestimonialsBlock.tsx # CRÉER
    ├── GalleryBlock.tsx     # CRÉER
    ├── CTABlock.tsx         # CRÉER
    └── HeaderBlock.tsx      # CRÉER (Basique)
```

### 5.2 Tests Smoke (Nouveau)

Créer `src/__tests__/components/BlockRenderer.test.tsx` pour vérifier que chaque block rend sans erreur :

```typescript
import { render } from '@testing-library/react';
import BlockRenderer from '@/components/BlockRenderer';
import { SiteSection } from '@/types/site-definition';

const mockSections: Record<string, SiteSection> = {
  hero: { 
      id: '1', type: 'hero', 
      content: { title: 'Test', subtitle: 'Sub', cta: { text: 'Go', link: '#' } } 
  },
  about: {
      id: '2', type: 'about',
      content: { title: 'About', description: 'Desc' }
  }
  // ... ajouter un mock minimal pour chaque type
};

describe('BlockRenderer', () => {
  Object.entries(mockSections).forEach(([type, section]) => {
    it(`renders ${type} without crashing`, () => {
      expect(() => render(<BlockRenderer section={section} />)).not.toThrow();
    });
  });
});
```

### 5.3 BlockRenderer Refactoré

```typescript
// src/components/BlockRenderer.tsx
import { SiteSection } from '@/types/site-definition';
import dynamic from 'next/dynamic';

// Import dynamique pour code splitting
const blockComponents = {
    header: dynamic(() => import('./blocks/HeaderBlock')),
    hero: dynamic(() => import('./blocks/HeroBlock')),
    about: dynamic(() => import('./blocks/AboutBlock')),
    services: dynamic(() => import('./blocks/ServicesBlock')),
    features: dynamic(() => import('./blocks/FeaturesBlock')),
    testimonials: dynamic(() => import('./blocks/TestimonialsBlock')),
    contact: dynamic(() => import('./blocks/ContactBlock')),
    gallery: dynamic(() => import('./blocks/GalleryBlock')),
    cta: dynamic(() => import('./blocks/CTABlock')),
    footer: dynamic(() => import('./blocks/FooterBlock')),
};

interface BlockRendererProps {
    section: SiteSection;
}

export default function BlockRenderer({ section }: BlockRendererProps) {
    const BlockComponent = blockComponents[section.type];
    
    if (!BlockComponent) {
        console.warn(`Unknown section type: ${section.type}`);
        return null;
    }
    
    return <BlockComponent {...section.content} />;
}
```

### 5.3 Composants à Créer

#### `AboutBlock.tsx`

```typescript
// src/components/blocks/AboutBlock.tsx
import { AboutSectionContent, AboutStat } from '@/types/blocks/about';

interface AboutBlockProps extends AboutSectionContent {}

export default function AboutBlock({
    title,
    subtitle,
    description,
    mission,
    vision,
    image,
    stats
}: AboutBlockProps) {
    return (
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
            <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    {/* Content */}
                    <div className="space-y-6">
                        <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
                            {title}
                        </h2>
                        {subtitle && (
                            <p className="text-xl text-blue-600 font-semibold">
                                {subtitle}
                            </p>
                        )}
                        <p className="text-lg text-gray-600 leading-relaxed">
                            {description}
                        </p>
                        
                        {mission && (
                            <div className="border-l-4 border-blue-500 pl-4">
                                <h3 className="font-semibold text-gray-900">Notre Mission</h3>
                                <p className="text-gray-600">{mission}</p>
                            </div>
                        )}
                        
                        {vision && (
                            <div className="border-l-4 border-green-500 pl-4">
                                <h3 className="font-semibold text-gray-900">Notre Vision</h3>
                                <p className="text-gray-600">{vision}</p>
                            </div>
                        )}
                    </div>
                    
                    {/* Image */}
                    {image && (
                        <div className="relative h-96 rounded-2xl overflow-hidden shadow-xl">
                            <img
                                src={image}
                                alt={title}
                                className="w-full h-full object-cover"
                            />
                        </div>
                    )}
                </div>
                
                {/* Stats */}
                {stats && stats.length > 0 && (
                    <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8">
                        {stats.map((stat, index) => (
                            <div key={index} className="text-center">
                                <div className="text-4xl font-bold text-blue-600">
                                    {stat.value}
                                </div>
                                <div className="text-gray-600 mt-1">
                                    {stat.label}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </section>
    );
}
```

#### `ServicesBlock.tsx`

```typescript
// src/components/blocks/ServicesBlock.tsx
import { ServicesSectionContent, ServiceItem } from '@/types/blocks/services';

interface ServicesBlockProps extends ServicesSectionContent {}

export default function ServicesBlock({
    title,
    subtitle,
    services,
    layout = 'grid'
}: ServicesBlockProps) {
    return (
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="text-center mb-16">
                    <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
                        {title}
                    </h2>
                    {subtitle && (
                        <p className="mt-4 text-xl text-gray-600">
                            {subtitle}
                        </p>
                    )}
                </div>
                
                {/* Services Grid */}
                <div className={`grid gap-8 ${
                    layout === 'grid' 
                        ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' 
                        : 'grid-cols-1'
                }`}>
                    {services.map((service) => (
                        <ServiceCard key={service.id} service={service} />
                    ))}
                </div>
            </div>
        </section>
    );
}

function ServiceCard({ service }: { service: ServiceItem }) {
    return (
        <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            {service.icon && (
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                    <span className="text-2xl">{service.icon}</span>
                </div>
            )}
            {service.image && (
                <img
                    src={service.image}
                    alt={service.title}
                    className="w-full h-48 object-cover rounded-lg mb-4"
                />
            )}
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {service.title}
            </h3>
            <p className="text-gray-600 mb-4">
                {service.description}
            </p>
            {service.price && (
                <p className="text-blue-600 font-semibold">
                    {service.price}
                </p>
            )}
            {service.href && (
                <a
                    href={service.href}
                    className="inline-block mt-4 text-blue-600 hover:text-blue-700 font-medium"
                >
                    En savoir plus →
                </a>
            )}
        </div>
    );
}
```

#### `ContactBlock.tsx`

```typescript
// src/components/blocks/ContactBlock.tsx
import { ContactSectionContent } from '@/types/blocks/contact';
import { useState } from 'react';

interface ContactBlockProps extends ContactSectionContent {}

export default function ContactBlock({
    title,
    subtitle,
    description,
    email,
    phone,
    address,
    socialLinks,
    showForm = true,
    formFields
}: ContactBlockProps) {
    const [formData, setFormData] = useState<Record<string, string>>({});
    
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        console.log('Form submitted:', formData);
        // TODO: Implement form submission
    };
    
    return (
        <section id="contact" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
            <div className="max-w-7xl mx-auto">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    {/* Contact Info */}
                    <div className="space-y-8">
                        <div>
                            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
                                {title}
                            </h2>
                            {subtitle && (
                                <p className="mt-2 text-xl text-gray-600">
                                    {subtitle}
                                </p>
                            )}
                            {description && (
                                <p className="mt-4 text-gray-600">
                                    {description}
                                </p>
                            )}
                        </div>
                        
                        <div className="space-y-4">
                            {email && (
                                <div className="flex items-center space-x-3">
                                    <span className="text-blue-600">📧</span>
                                    <a href={`mailto:${email}`} className="text-gray-600 hover:text-blue-600">
                                        {email}
                                    </a>
                                </div>
                            )}
                            {phone && (
                                <div className="flex items-center space-x-3">
                                    <span className="text-blue-600">📞</span>
                                    <a href={`tel:${phone}`} className="text-gray-600 hover:text-blue-600">
                                        {phone}
                                    </a>
                                </div>
                            )}
                            {address && (
                                <div className="flex items-start space-x-3">
                                    <span className="text-blue-600">📍</span>
                                    <div className="text-gray-600">
                                        <p>{address.street}</p>
                                        <p>{address.city}, {address.country}</p>
                                    </div>
                                </div>
                            )}
                        </div>
                        
                        {/* Social Links */}
                        {socialLinks && socialLinks.length > 0 && (
                            <div className="flex space-x-4">
                                {socialLinks.map((link, index) => (
                                    <a
                                        key={index}
                                        href={link.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center hover:bg-blue-100 transition-colors"
                                    >
                                        {link.platform[0].toUpperCase()}
                                    </a>
                                ))}
                            </div>
                        )}
                    </div>
                    
                    {/* Contact Form */}
                    {showForm && (
                        <form onSubmit={handleSubmit} className="space-y-6 bg-gray-50 p-8 rounded-xl">
                            {(formFields || [
                                { name: 'name', type: 'text', label: 'Nom', required: true },
                                { name: 'email', type: 'email', label: 'Email', required: true },
                                { name: 'message', type: 'textarea', label: 'Message', required: true }
                            ]).map((field) => (
                                <div key={field.name}>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        {field.label} {field.required && '*'}
                                    </label>
                                    {field.type === 'textarea' ? (
                                        <textarea
                                            name={field.name}
                                            required={field.required}
                                            placeholder={field.placeholder}
                                            rows={4}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            onChange={(e) => setFormData({...formData, [field.name]: e.target.value})}
                                        />
                                    ) : (
                                        <input
                                            type={field.type}
                                            name={field.name}
                                            required={field.required}
                                            placeholder={field.placeholder}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            onChange={(e) => setFormData({...formData, [field.name]: e.target.value})}
                                        />
                                    )}
                                </div>
                            ))}
                            <button
                                type="submit"
                                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                            >
                                Envoyer
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </section>
    );
}
```

#### `CTABlock.tsx`

```typescript
// src/components/blocks/CTABlock.tsx
import { CTASectionContent } from '@/types/blocks/cta';

interface CTABlockProps extends CTASectionContent {}

export default function CTABlock({
    headline,
    description,
    primaryButton,
    secondaryButton,
    backgroundColor,
    backgroundImage
}: CTABlockProps) {
    return (
        <section
            className="py-20 px-4 sm:px-6 lg:px-8 relative"
            style={{
                backgroundColor: backgroundColor || '#3B82F6',
                backgroundImage: backgroundImage ? `url(${backgroundImage})` : undefined,
                backgroundSize: 'cover',
                backgroundPosition: 'center'
            }}
        >
            {backgroundImage && (
                <div className="absolute inset-0 bg-black/50" />
            )}
            
            <div className="max-w-4xl mx-auto text-center relative z-10">
                <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                    {headline}
                </h2>
                {description && (
                    <p className="text-xl text-white/90 mb-8">
                        {description}
                    </p>
                )}
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <a
                        href={primaryButton.href}
                        className={`px-8 py-3 rounded-lg font-semibold transition-colors ${
                            primaryButton.variant === 'outline'
                                ? 'border-2 border-white text-white hover:bg-white hover:text-blue-600'
                                : 'bg-white text-blue-600 hover:bg-gray-100'
                        }`}
                    >
                        {primaryButton.text}
                    </a>
                    
                    {secondaryButton && (
                        <a
                            href={secondaryButton.href}
                            className="px-8 py-3 rounded-lg font-semibold border-2 border-white text-white hover:bg-white/10 transition-colors"
                        >
                            {secondaryButton.text}
                        </a>
                    )}
                </div>
            </div>
        </section>
    );
}
```

#### `TestimonialsBlock.tsx`

```typescript
// src/components/blocks/TestimonialsBlock.tsx
import { TestimonialsSectionContent, TestimonialItem } from '@/types/blocks/testimonials';

interface TestimonialsBlockProps extends TestimonialsSectionContent {}

export default function TestimonialsBlock({
    title,
    subtitle,
    testimonials,
    layout = 'grid'
}: TestimonialsBlockProps) {
    return (
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-16">
                    <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
                        {title}
                    </h2>
                    {subtitle && (
                        <p className="mt-4 text-xl text-gray-600">
                            {subtitle}
                        </p>
                    )}
                </div>
                
                <div className={`grid gap-8 ${
                    layout === 'grid'
                        ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
                        : 'grid-cols-1 max-w-2xl mx-auto'
                }`}>
                    {testimonials.map((testimonial) => (
                        <TestimonialCard key={testimonial.id} testimonial={testimonial} />
                    ))}
                </div>
            </div>
        </section>
    );
}

function TestimonialCard({ testimonial }: { testimonial: TestimonialItem }) {
    return (
        <div className="bg-white p-6 rounded-xl shadow-lg">
            {/* Rating */}
            {testimonial.rating && (
                <div className="flex mb-4">
                    {[...Array(5)].map((_, i) => (
                        <span
                            key={i}
                            className={i < testimonial.rating! ? 'text-yellow-400' : 'text-gray-300'}
                        >
                            ★
                        </span>
                    ))}
                </div>
            )}
            
            {/* Quote */}
            <blockquote className="text-gray-600 italic mb-6">
                "{testimonial.quote}"
            </blockquote>
            
            {/* Author */}
            <div className="flex items-center">
                {testimonial.avatar && (
                    <img
                        src={testimonial.avatar}
                        alt={testimonial.author}
                        className="w-12 h-12 rounded-full object-cover mr-4"
                    />
                )}
                <div>
                    <p className="font-semibold text-gray-900">
                        {testimonial.author}
                    </p>
                    {(testimonial.role || testimonial.company) && (
                        <p className="text-sm text-gray-500">
                            {testimonial.role}{testimonial.role && testimonial.company && ', '}
                            {testimonial.company}
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
```

#### `GalleryBlock.tsx`

```typescript
// src/components/blocks/GalleryBlock.tsx
import { GallerySectionContent, GalleryImage } from '@/types/blocks/gallery';

interface GalleryBlockProps extends GallerySectionContent {}

export default function GalleryBlock({
    title,
    subtitle,
    images,
    layout = 'grid',
    columns = 3
}: GalleryBlockProps) {
    const gridCols = {
        2: 'grid-cols-1 sm:grid-cols-2',
        3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
        4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
    };
    
    return (
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
            <div className="max-w-7xl mx-auto">
                {(title || subtitle) && (
                    <div className="text-center mb-12">
                        {title && (
                            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
                                {title}
                            </h2>
                        )}
                        {subtitle && (
                            <p className="mt-4 text-xl text-gray-600">
                                {subtitle}
                            </p>
                        )}
                    </div>
                )}
                
                <div className={`grid ${gridCols[columns]} gap-4`}>
                    {images.map((image) => (
                        <GalleryItem key={image.id} image={image} />
                    ))}
                </div>
            </div>
        </section>
    );
}

function GalleryItem({ image }: { image: GalleryImage }) {
    const content = (
        <div className="relative group overflow-hidden rounded-lg">
            <img
                src={image.src}
                alt={image.alt}
                className="w-full h-64 object-cover transition-transform group-hover:scale-105"
            />
            {image.caption && (
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-end">
                    <p className="text-white p-4">{image.caption}</p>
                </div>
            )}
        </div>
    );
    
    if (image.href) {
        return (
            <a href={image.href} className="block">
                {content}
            </a>
        );
    }
    
    return content;
}
```

### 5.4 PageRenderer & SiteRenderer

#### `PageRenderer.tsx`

```typescript
// src/components/PageRenderer.tsx
import { SitePage } from '@/types/site-definition';
import BlockRenderer from './BlockRenderer';

interface PageRendererProps {
    page: SitePage;
}

export default function PageRenderer({ page }: PageRendererProps) {
    return (
        <main>
            {page.sections.map((section) => (
                <BlockRenderer key={section.id} section={section} />
            ))}
        </main>
    );
}
```

#### `SiteRenderer.tsx`

```typescript
// src/components/SiteRenderer.tsx
import { SiteDefinition } from '@/types/site-definition';
import PageRenderer from './PageRenderer';
import ThemeProvider from './ThemeProvider';

interface SiteRendererProps {
    site: SiteDefinition;
    currentPageSlug?: string;
}

export default function SiteRenderer({ site, currentPageSlug = '/' }: SiteRendererProps) {
    const currentPage = site.pages.find(p => p.slug === currentPageSlug) || site.pages[0];
    
    if (!currentPage) {
        return <div>Page not found</div>;
    }
    
    return (
        <ThemeProvider theme={site.theme}>
            <PageRenderer page={currentPage} />
        </ThemeProvider>
    );
}
```

#### `ThemeProvider.tsx`

```typescript
// src/components/ThemeProvider.tsx
import { SiteTheme } from '@/types/site-definition';
import { ReactNode } from 'react';

interface ThemeProviderProps {
    theme: SiteTheme;
    children: ReactNode;
}

export default function ThemeProvider({ theme, children }: ThemeProviderProps) {
    const cssVariables = {
        '--color-primary': theme.colors.primary,
        '--color-secondary': theme.colors.secondary,
        '--color-accent': theme.colors.accent || theme.colors.primary,
        '--color-background': theme.colors.background,
        '--color-text': theme.colors.text,
        '--font-heading': theme.fonts.heading,
        '--font-body': theme.fonts.body,
    } as React.CSSProperties;
    
    return (
        <div style={cssVariables}>
            {children}
        </div>
    );
}
```

---

## 6. Workflow Git

### 6.1 Créer ta branche

```bash
cd c:\genesis
git checkout master
git pull origin master
git checkout -b feature/gen-9-block-renderer
```

### 6.2 Commits recommandés

```bash
# Après chaque composant
git add genesis-frontend/src/components/blocks/AboutBlock.tsx
git commit -m "feat(blocks): Add AboutBlock component"

git add genesis-frontend/src/components/blocks/ServicesBlock.tsx
git commit -m "feat(blocks): Add ServicesBlock component with grid layout"

# À la fin
git add genesis-frontend/src/components/
git commit -m "feat(renderer): Add PageRenderer, SiteRenderer, and ThemeProvider"
```

### 6.3 Push et PR

```bash
git push origin feature/gen-9-block-renderer
```

Créer une **Pull Request** vers `master` avec :
- Titre : `feat(renderer): [GEN-9] Complete Block Renderer with all components`
- Reviewer : Tech Lead Genesis (Cascade)

---

## 7. Critères d'Acceptation

- [ ] **Tous les blocks** créés : About, Services, Contact, Testimonials, Gallery, CTA
- [ ] **BlockRenderer** refactoré avec map dynamique
- [ ] **PageRenderer** et **SiteRenderer** fonctionnels
- [ ] **ThemeProvider** applique les couleurs CSS variables
- [ ] **TypeScript** : Pas d'erreurs (`npm run build`)
- [ ] **Props** conformes aux types GEN-8
- [ ] **PR** créée et prête pour review

---

## 8. Ressources

| Document | Chemin |
|----------|--------|
| Types TypeScript (GEN-8) | `genesis-frontend/src/types/blocks/*.ts` |
| Blocks existants | `genesis-frontend/src/components/blocks/` |
| Brief Tech Lead Sprint 5 | `docs/memo/MEMO_BRIEF_TECH_LEAD_SPRINT5_2025-12-02.md` |

---

## 9. Points de Contact

| Rôle | Contact | Pour |
|------|---------|------|
| **Tech Lead Genesis** | Cascade (via IDE) | Questions techniques, review PR |
| **Scrum Master** | Via Cascade | Clarifications fonctionnelles |

---

**Bonne implémentation !**

*— Tech Lead Genesis AI (Cascade)*
