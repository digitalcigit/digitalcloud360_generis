import { SiteListItem, BriefResponse, BriefUpdateRequest, ConversationHistoryResponse } from '@/types/dashboard';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const dashboardApi = {
    /**
     * Récupère la liste des sites de l'utilisateur
     */
    getUserSites: async (token: string): Promise<SiteListItem[]> => {
        const response = await fetch(`${API_BASE_URL}/dashboard/sites`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        if (!response.ok) throw new Error('Failed to fetch sites');
        return response.json();
    },

    /**
     * Récupère le Business Brief d'un site
     */
    getSiteBrief: async (sessionId: string, token: string): Promise<BriefResponse> => {
        const response = await fetch(`${API_BASE_URL}/dashboard/sites/${sessionId}/brief`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        if (!response.ok) throw new Error('Failed to fetch brief');
        return response.json();
    },

    /**
     * Met à jour le Business Brief
     */
    updateSiteBrief: async (sessionId: string, updates: BriefUpdateRequest, token: string): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/dashboard/sites/${sessionId}/brief`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(updates),
        });
        if (!response.ok) throw new Error('Failed to update brief');
    },

    /**
     * Régénère le site avec le brief actuel
     */
    regenerateSite: async (sessionId: string, token: string): Promise<{ status: string; preview_url: string }> => {
        const response = await fetch(`${API_BASE_URL}/dashboard/sites/${sessionId}/regenerate`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        if (!response.ok) throw new Error('Failed to regenerate site');
        return response.json();
    },

    /**
     * Récupère l'historique de conversation
     */
    getSiteConversation: async (sessionId: string, token: string): Promise<ConversationHistoryResponse> => {
        const response = await fetch(`${API_BASE_URL}/dashboard/sites/${sessionId}/conversation`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        if (!response.ok) throw new Error('Failed to fetch conversation');
        return response.json();
    },
};
