import { SiteDefinition } from '@/types/site-definition';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface GenerateSiteResponse {
    site_id: number;
    status: string;
}

export async function generateSite(briefId: number, token: string): Promise<GenerateSiteResponse> {
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

export async function getSite(siteId: number, token: string): Promise<SiteDefinition> {
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
