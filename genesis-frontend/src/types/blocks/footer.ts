export interface FooterSectionContent {
    logo?: string;
    companyName?: string;        // Optional pour compatibilité
    description?: string;
    columns?: FooterColumn[];
    copyright: string;           // Required, aligné sur FooterBlock.tsx
    socialLinks?: SocialLink[];
    links?: FooterLink[];        // Aligné sur FooterBlock.tsx (pas legalLinks)
}

export interface FooterColumn {
    title: string;
    links: FooterLink[];
}

export interface FooterLink {
    text: string;
    url: string;                 // Aligné sur FooterBlock.tsx (pas href)
}

// Réutiliser SocialLink de contact.ts
export type { SocialLink } from './contact';
