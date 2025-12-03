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
