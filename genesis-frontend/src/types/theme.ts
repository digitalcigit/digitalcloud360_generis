export interface Theme {
    id: number;
    name: string;
    slug: string;
    description: string;
    category: string;
    thumbnail_url: string;
    preview_url?: string;
    is_premium: boolean;
    compatibility_tags: string[];
    features: Record<string, any>;
}

export interface ThemeRecommendation {
    theme: Theme;
    match_score: number;
    reasoning: string;
}

export interface ThemeRecommendationList {
    brief_id: number;
    recommendations: ThemeRecommendation[];
}
