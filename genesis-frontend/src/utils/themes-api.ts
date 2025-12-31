import { ThemeRecommendationList } from '@/types/theme';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const themesApi = {
    getRecommendations: async (token: string, briefId: number): Promise<ThemeRecommendationList> => {
        const response = await fetch(`${API_BASE_URL}/themes/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ brief_id: briefId })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get recommendations');
        }

        return response.json();
    },

    selectTheme: async (token: string, briefId: number, themeId: number): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/themes/select`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ brief_id: briefId, theme_id: themeId })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to select theme');
        }

        return response.json();
    }
};
