import { SiteDefinition } from '@/types/site-definition';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface SiteResponse {
    site_id: string;
    brief_id: string;
    user_id: number;
    site_definition: SiteDefinition;
    created_at: string;
}

export async function generateSite(briefId: number | string, token: string): Promise<SiteResponse> {
    const response = await fetch(`${API_BASE_URL}/sites/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ brief_id: briefId }),
    });

    if (!response.ok) {
        throw new Error('Failed to generate site');
    }

    return response.json();
}

export async function getSite(siteId: string, token: string): Promise<SiteResponse> {
    const response = await fetch(`${API_BASE_URL}/sites/${siteId}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        throw new Error('Failed to fetch site');
    }

    return response.json();
}

export async function getSitePreview(siteId: string, token: string): Promise<SiteDefinition> {
    const response = await fetch(`${API_BASE_URL}/sites/${siteId}/preview`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        throw new Error('Failed to fetch site preview');
    }

    return response.json();
}

export async function getCoachingSite(sessionId: string, token: string): Promise<SiteDefinition> {
    const response = await fetch(`${API_BASE_URL}/coaching/${sessionId}/site`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        throw new Error('Failed to fetch coaching site');
    }

    return response.json();
}
