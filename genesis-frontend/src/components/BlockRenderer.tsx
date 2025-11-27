import { SiteSection } from '@/types/site-definition';
import HeroBlock from './blocks/HeroBlock';
import FeaturesBlock from './blocks/FeaturesBlock';
import FooterBlock from './blocks/FooterBlock';

interface BlockRendererProps {
    section: SiteSection;
}

export default function BlockRenderer({ section }: BlockRendererProps) {
    switch (section.type) {
        case 'hero':
            return (
                <HeroBlock
                    title={section.content.title}
                    subtitle={section.content.subtitle}
                    image={section.content.image}
                    cta={section.content.cta}
                />
            );

        case 'features':
            return (
                <FeaturesBlock
                    title={section.content.title}
                    features={section.content.features}
                />
            );

        case 'footer':
            return (
                <FooterBlock
                    copyright={section.content.copyright}
                    links={section.content.links}
                />
            );

        default:
            console.warn(`Unknown section type: ${section.type}`);
            return null;
    }
}
