export interface HeroSectionContent {
    title: string;              // Aligné sur HeroBlock.tsx
    subtitle: string;           // Aligné sur HeroBlock.tsx (Required)
    description?: string;
    image?: string;             // Aligné sur HeroBlock.tsx (pas backgroundImage)
    backgroundVideo?: string;
    cta?: HeroCTA;              // Single object, aligné sur HeroBlock.tsx
    alignment?: 'left' | 'center' | 'right';
    overlay?: boolean;
}

export interface HeroCTA {
    text: string;
    link: string;               // Aligné sur HeroBlock.tsx (pas href)
    variant?: 'primary' | 'secondary' | 'outline';
}
