import { SocialLink } from './contact';

export interface FooterSectionContent {
    variant?: 'simple' | 'restaurant';
    logo?: string;
    companyName?: string;        
    description?: string;
    columns?: FooterColumn[];
    copyright: string;           
    socialLinks?: SocialLink[];
    links?: FooterLink[];        
    // V2 Properties for Restaurant Theme
    openingHours?: OpeningHours[];
    newsletter?: {
        title: string;
        description: string;
        placeholder: string;
        buttonText: string;
    };
    contactInfo?: {
        address?: string;
        phone?: string;
        email?: string;
    };
}

export interface OpeningHours {
    days: string;
    hours: string;
}

export interface FooterColumn {
    title: string;
    links: FooterLink[];
}

export interface FooterLink {
    text: string;
    url: string;                 
}

// Réutiliser SocialLink de contact.ts
export type { SocialLink } from './contact';
