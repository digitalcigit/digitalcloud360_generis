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
