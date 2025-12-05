import { SiteSection } from '@/types/site-definition';
import dynamic from 'next/dynamic';
import { ComponentType } from 'react';

// Import dynamique pour code splitting et éviter de charger tous les blocks
const blockComponents: Record<string, ComponentType<any>> = {
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

    return (
        <section id={section.id} className={section.styles?.className}>
            <BlockComponent {...section.content} />
        </section>
    );
}
