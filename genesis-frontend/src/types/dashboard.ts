export interface SiteListItem {
    session_id: string;
    business_name: string;
    sector: string;
    theme_slug?: string | null;
    preview_url: string;
    status: 'ready' | 'expired';
    created_at: string;
    updated_at?: string | null;
    hero_image_url?: string | null;
}

export interface BriefResponse {
    session_id: string;
    business_name: string;
    vision: string;
    mission: string;
    target_audience: string;
    differentiation: string;
    value_proposition: string;
    sector: string;
    location?: any;
    logo_url?: string | null;
    created_at: string;
    updated_at?: string | null;
    market_research_summary?: any;
}

export interface BriefUpdateRequest {
    business_name?: string;
    vision?: string;
    mission?: string;
    target_audience?: string;
    differentiation?: string;
    value_proposition?: string;
}

export interface ConversationMessage {
    role: string;
    content: string;
    timestamp?: string | null;
}

export interface ConversationHistoryResponse {
    session_id: string;
    messages: ConversationMessage[];
}
