export interface TestimonialsSectionContent {
    title: string;
    subtitle?: string;
    testimonials: TestimonialItem[];
    layout?: 'carousel' | 'grid' | 'masonry';
}

export interface TestimonialItem {
    id: string;
    quote: string;
    author: string;
    role?: string;
    company?: string;
    avatar?: string;
    rating?: number;
}
