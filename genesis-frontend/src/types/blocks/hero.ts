export interface HeroSectionContent {
    title: string;
    subtitle: string;
    description?: string;
    image?: string;
    backgroundVideo?: string;
    cta?: HeroCTA;
    alignment?: 'left' | 'center' | 'right';
    overlay?: boolean;
    // V2 Properties
    variant?: 'standard' | 'split' | 'slider';
    slides?: HeroSlide[];
}

export interface HeroSlide {
    title: string;
    subtitle?: string;
    image: string;
    cta?: HeroCTA;
}

export interface HeroCTA {
    text: string;
    link: string;
    variant?: 'primary' | 'secondary' | 'outline';
}
