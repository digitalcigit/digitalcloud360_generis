import {
    BlockContentMap,
    BlockType,
    SiteSection,
    SectionStyles,
    SiteSectionGeneric
} from '@/types/site-definition';
import dynamic from 'next/dynamic';
import { ComponentType } from 'react';

type BlockComponentMap = {
    [K in BlockType]: ComponentType<BlockContentMap[K]>;
};

type UnknownSection = {
    id: string;
    type: string;
    content: Record<string, unknown>;
    styles?: SectionStyles;
};

// Import dynamique pour code splitting et éviter de charger tous les blocks
const blockComponents: BlockComponentMap = {
    header: dynamic<BlockContentMap['header']>(() => import('./blocks/HeaderBlock')),
    hero: dynamic<BlockContentMap['hero']>(() => import('./blocks/HeroBlock')),
    about: dynamic<BlockContentMap['about']>(() => import('./blocks/AboutBlock')),
    services: dynamic<BlockContentMap['services']>(() => import('./blocks/ServicesBlock')),
    features: dynamic<BlockContentMap['features']>(() => import('./blocks/FeaturesBlock')),
    testimonials: dynamic<BlockContentMap['testimonials']>(() => import('./blocks/TestimonialsBlock')),
    contact: dynamic<BlockContentMap['contact']>(() => import('./blocks/ContactBlock')),
    gallery: dynamic<BlockContentMap['gallery']>(() => import('./blocks/GalleryBlock')),
    cta: dynamic<BlockContentMap['cta']>(() => import('./blocks/CTABlock')),
    footer: dynamic<BlockContentMap['footer']>(() => import('./blocks/FooterBlock')),
    menu: dynamic<BlockContentMap['menu']>(() => import('./blocks/MenuBlock')),
};

const isKnownSection = (section: SiteSection | UnknownSection): section is SiteSection =>
    (section.type as string) in blockComponents;

interface BlockRendererProps {
    section: SiteSection | UnknownSection;
}

export default function BlockRenderer({ section }: BlockRendererProps) {
    if (!isKnownSection(section)) {
        console.warn(`Unknown section type: ${section.type}`);
        return null;
    }

    return renderKnownSection(section);
}

function renderKnownSection<T extends BlockType>(section: SiteSectionGeneric<T>) {
    const BlockComponent = blockComponents[section.type] as ComponentType<BlockContentMap[T]>;
    return (
        <section id={section.id} className={section.styles?.className}>
            <BlockComponent {...(section.content as BlockContentMap[T])} />
        </section>
    );
}
